"""退款服务：退款校验 + 调用支付 Provider + 状态更新 + 库存回滚。"""
from __future__ import annotations

import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import utc_now
from app.core.errors import BizError, ErrorCode
from app.core.tenant import TenantContext
from app.models.catalog import GroupBuyPackage
from app.models.order import Order, Refund
from app.schemas.order import RefundApplyIn
from app.services.payment.factory import get_payment_provider


def generate_refund_no() -> str:
    """生成唯一退款单号。"""
    return "RF" + utc_now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper()


async def apply_refund(db: AsyncSession, ctx: TenantContext, data: RefundApplyIn) -> Refund:
    """申请退款（全额/部分），调用支付 Provider，状态机与库存回滚。"""
    if ctx.typ != "consumer":
        raise BizError(ErrorCode.NO_PERMISSION, "仅消费者可申请退款")

    order = await db.scalar(select(Order).where(Order.order_no == data.order_no))
    if order is None:
        raise BizError(ErrorCode.ORDER_NOT_FOUND)
    if order.consumer_id != ctx.user_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)

    # 幂等拒绝：已存在退款单（含已成功），优先于状态校验返回 REFUND_FAILED。
    # 否则已退款订单会因状态不在 (paid/fulfilled) 而误报 ORDER_STATUS_INVALID。
    existing = await db.scalar(
        select(Refund).where(
            Refund.order_id == order.id,
            Refund.status.in_(["pending", "processing", "succeeded"]),
        )
    )
    if existing is not None:
        raise BizError(ErrorCode.REFUND_FAILED, "该订单已存在退款")

    if order.status not in ("paid", "fulfilled"):
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "订单状态不可退款")

    if data.amount > order.total_amount:
        raise BizError(ErrorCode.REFUND_FAILED, "退款金额超过订单总额")

    refund = Refund(
        refund_no=generate_refund_no(),
        order_id=order.id,
        consumer_id=order.consumer_id,
        merchant_id=order.merchant_id,
        amount=data.amount,
        reason=data.reason,
        status="processing",
    )
    db.add(refund)
    await db.flush()

    provider = get_payment_provider()
    try:
        channel_refund_id = await provider.refund(order, data.amount)
    except BizError as exc:  # pragma: no cover - 真实渠道异常路径
        refund.status = "failed"
        await db.commit()
        await db.refresh(refund)
        raise exc

    refund.status = "succeeded"
    refund.channel_refund_id = channel_refund_id

    # 回滚库存
    package = await db.scalar(
        select(GroupBuyPackage).where(GroupBuyPackage.id == order.package_id)
    )
    if package is not None:
        package.sold_count = max(0, package.sold_count - order.quantity)

    order.status = "refunded"

    await db.commit()
    await db.refresh(refund)
    return refund
