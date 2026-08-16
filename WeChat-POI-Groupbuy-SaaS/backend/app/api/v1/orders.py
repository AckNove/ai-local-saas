"""订单 API：下单 / 列表 / 详情 / 支付回调 / 自提状态更新。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok, paginate
from app.core.tenant import (
    ROLE_CONSUMER,
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    ROLE_VERIFIER,
    TenantContext,
    get_tenant_context,
    require_role,
    tenant_filter,
)
from app.models.order import Order, VerificationCode
from app.schemas.order import OrderCreate, OrderOut, PickupUpdateIn, VerificationCodeOut
from app.services.order import close_expired_orders, create_order, pay_notify

router = APIRouter(prefix="/orders", tags=["orders"])


async def _order_out(db: AsyncSession, o: Order, with_codes: bool = False) -> dict:
    codes = []
    if with_codes:
        vcs = (await db.scalars(
            select(VerificationCode).where(VerificationCode.order_id == o.id)
        )).all()
        codes = [
            VerificationCodeOut(
                id=v.id, code=v.code, status=v.status, expires_at=_iso(v.expires_at)
            ).model_dump()
            for v in vcs
        ]
    return OrderOut(
        id=o.id, order_no=o.order_no, consumer_id=o.consumer_id, merchant_id=o.merchant_id,
        store_id=o.store_id, package_id=o.package_id, quantity=o.quantity,
        unit_price=o.unit_price, total_amount=o.total_amount, commission_amount=o.commission_amount,
        status=o.status, fulfillment_type=o.fulfillment_type, pickup_status=o.pickup_status,
        source=o.source, channel_binding_id=o.channel_binding_id, paid_at=_iso(o.paid_at),
        expires_at=_iso(o.expires_at), phone=o.phone, created_at=_iso(o.created_at),
        verification_codes=codes,
    ).model_dump()


@router.post("")
async def create_order_api(
    body: OrderCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_CONSUMER)),
):
    order, pay_params = await create_order(db, ctx, body)
    return ok({"order": await _order_out(db, order), "pay_params": pay_params})


@router.get("")
async def list_orders(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
    status: str | None = Query(None),
    keyword: str | None = Query(None, description="订单号/手机号模糊搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Order).where(Order.deleted_at.is_(None))
    if ctx.is_consumer:
        stmt = stmt.where(Order.consumer_id == ctx.user_id)
    else:
        stmt = tenant_filter(stmt, Order, ctx)
    if status:
        stmt = stmt.where(Order.status == status)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            (Order.order_no.like(like)) | (Order.phone.like(like))
        )

    total = int(await db.scalar(
        select(func.count()).select_from(stmt.subquery())
    ) or 0)
    stmt = stmt.order_by(Order.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([await _order_out(db, o) for o in rows], total, page, page_size))


@router.get("/{order_no}")
async def get_order(
    order_no: str,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    o = await db.scalar(select(Order).where(Order.order_no == order_no))
    if o is None or o.deleted_at is not None:
        raise BizError(ErrorCode.ORDER_NOT_FOUND)
    if ctx.is_consumer and o.consumer_id != ctx.user_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    if not ctx.is_consumer and not ctx.is_platform and o.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    return ok(await _order_out(db, o, with_codes=True))


@router.post("/{order_no}/pay-notify")
async def pay_notify_api(
    order_no: str,
    body: dict | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Mock 支付回调（幂等）。真实环境由微信支付服务器回调，验签后调用。"""
    transaction_id = (body or {}).get("transaction_id")
    order = await pay_notify(db, order_no, transaction_id)
    return ok(await _order_out(db, order, with_codes=True))


@router.patch("/{order_no}/pickup")
async def pickup_update_api(
    order_no: str, body: PickupUpdateIn,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(
        require_role(ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER, ROLE_PLATFORM)
    ),
):
    from app.services.fulfillment import update_pickup_status

    order = await update_pickup_status(db, ctx, order_no, body.status)
    return ok(await _order_out(db, order, with_codes=True))


@router.post("/admin/close-expired")
async def close_expired_api(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM)),
):
    count = await close_expired_orders(db)
    return ok({"closed": count})


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None
