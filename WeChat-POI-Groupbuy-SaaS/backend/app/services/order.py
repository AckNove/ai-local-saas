"""交易核心服务：下单、支付回调（状态机 + 核销码生成）、超时关闭。"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import as_utc, utc_now
from app.core.errors import BizError, ErrorCode
from app.core.tenant import TenantContext
from app.models.catalog import GroupBuyPackage, PackageStore
from app.models.order import Order, OrderItem, VerificationCode
from app.models.tenant import Consumer, Store
from app.schemas.order import OrderCreate
from app.services.payment.factory import get_payment_provider


def generate_order_no() -> str:
    """生成唯一订单号：PO + 时间 + 随机。"""
    return "PO" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper()


def generate_verify_code() -> str:
    """生成全局唯一的核销码（大写）。"""
    return secrets.token_hex(8).upper()


async def _unique_order_no(db: AsyncSession) -> str:
    for _ in range(5):
        no = generate_order_no()
        existing = await db.scalar(select(Order).where(Order.order_no == no))
        if existing is None:
            return no
    raise BizError(ErrorCode.SYSTEM_ERROR, "订单号生成失败")


async def create_order(
    db: AsyncSession, ctx: TenantContext, data: OrderCreate
) -> Order:
    """创建待支付订单，预占校验 + 调用支付 Provider 获取 pay_params。

    库存策略：下单校验 available = stock - sold_count；支付成功才正式扣 sold_count。
    """
    if ctx.typ != "consumer":
        raise BizError(ErrorCode.NO_PERMISSION, "仅消费者可下单")

    package = await db.scalar(
        select(GroupBuyPackage).where(GroupBuyPackage.id == data.package_id)
    )
    if package is None or package.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "套餐不存在")
    if package.status != "published":
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "套餐未上架")
    now = utc_now()
    if package.valid_to is not None and as_utc(package.valid_to) < now:
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "套餐已过期")

    store = await db.scalar(select(Store).where(Store.id == data.store_id))
    if store is None or store.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "门店不存在")
    if store.merchant_id != package.merchant_id:
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "门店不属于该套餐商户")

    available = package.stock - package.sold_count
    if data.quantity > available:
        raise BizError(ErrorCode.STOCK_NOT_ENOUGH)

    unit_price = package.group_price
    total = unit_price * data.quantity
    commission = int(total * settings.COMMISSION_RATE)

    order = Order(
        order_no=await _unique_order_no(db),
        consumer_id=ctx.user_id,
        merchant_id=package.merchant_id,
        store_id=store.id,
        package_id=package.id,
        quantity=data.quantity,
        unit_price=unit_price,
        total_amount=total,
        commission_amount=commission,
        status="pending_payment",
        fulfillment_type=data.fulfillment_type,
        source="video_channel" if data.channel_binding_id else "in_store",
        channel_binding_id=data.channel_binding_id,
        phone=data.phone,
        expires_at=now + timedelta(minutes=settings.PAY_TIMEOUT_MINUTES),
    )
    db.add(order)
    await db.flush()

    db.add(
        OrderItem(
            order_id=order.id,
            package_id=package.id,
            store_id=store.id,
            quantity=data.quantity,
            unit_price=unit_price,
        )
    )

    provider = get_payment_provider()
    pay_params = await provider.create_prepay(order)
    order.prepay_id = pay_params.get("prepay_id")
    order.idempotency_key = order.order_no  # 支付回调去重键

    await db.commit()
    await db.refresh(order)
    return order, pay_params


async def pay_notify(
    db: AsyncSession, order_no: str, transaction_id: str | None = None
) -> Order:
    """支付回调：幂等（按 idempotency_key 去重），状态机 pending→paid，生成核销码。

    返回已支付的订单对象；若已支付则直接幂等返回。
    """
    order = await db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None:
        raise BizError(ErrorCode.ORDER_NOT_FOUND)

    # 幂等：已支付/已核销直接返回
    if order.status in ("paid", "fulfilled"):
        return order
    if order.status != "pending_payment":
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "订单状态不可支付")

    # 正式扣减库存
    package = await db.scalar(
        select(GroupBuyPackage).where(GroupBuyPackage.id == order.package_id)
    )
    if package is not None:
        package.sold_count += order.quantity

    order.status = "paid"
    order.paid_at = utc_now()
    order.transaction_id = transaction_id or ("MOCK_TXN_" + secrets.token_hex(8).upper())

    # 自提订单初始备餐状态
    if order.fulfillment_type == "self_pickup":
        order.pickup_status = "preparing"

    # 生成核销码（dine_in / self_pickup；reservation 无需核销码）
    if order.fulfillment_type in ("dine_in", "self_pickup"):
        await _generate_verify_codes(db, order, package)

    await db.commit()
    await db.refresh(order)
    return order


async def _generate_verify_codes(
    db: AsyncSession, order: Order, package: GroupBuyPackage | None
) -> None:
    """为订单生成 quantity 个核销码（每个代表一件）。"""
    now = utc_now()
    expire_limit = now + timedelta(days=settings.VERIFY_CODE_EXPIRE_DAYS)
    # 核销码有效期 = min(套餐 valid_to, 支付后+30天)
    expires_at = expire_limit
    if package is not None and package.valid_to is not None and as_utc(package.valid_to) < expires_at:
        expires_at = package.valid_to

    for _ in range(order.quantity):
        code = generate_verify_code()
        db.add(
            VerificationCode(
                code=code,
                order_id=order.id,
                merchant_id=order.merchant_id,
                store_id=order.store_id,
                status="unused",
                expires_at=expires_at,
            )
        )


async def close_expired_orders(db: AsyncSession) -> int:
    """关闭超时未支付订单（支付超时回滚由状态表达，库存未扣故无需回滚）。"""
    now = utc_now()
    stmt = select(Order).where(
        Order.status == "pending_payment",
        Order.expires_at.is_not(None),
        as_utc(Order.expires_at) < now,
    )
    orders = (await db.scalars(stmt)).all()
    count = 0
    for o in orders:
        o.status = "closed"
        count += 1
    if count:
        await db.commit()
    return count
