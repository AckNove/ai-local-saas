"""退款 API：申请退款 + 查询。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok
from app.core.tenant import ROLE_CONSUMER, TenantContext, get_tenant_context, require_role
from app.models.order import Refund
from app.schemas.order import RefundApplyIn, RefundOut
from app.services.refund import apply_refund

router = APIRouter(prefix="/refunds", tags=["refunds"])


@router.post("")
async def apply_refund_api(
    body: RefundApplyIn,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_CONSUMER)),
):
    refund = await apply_refund(db, ctx, body)
    return ok(_refund_out(refund))


@router.get("/{refund_no}")
async def get_refund_api(
    refund_no: str,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    r = await db.scalar(select(Refund).where(Refund.refund_no == refund_no))
    if r is None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "退款单不存在")
    if ctx.is_consumer and r.consumer_id != ctx.user_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    if not ctx.is_consumer and not ctx.is_platform and r.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    return ok(_refund_out(r))


def _refund_out(r: Refund) -> dict:
    return RefundOut(
        id=r.id, refund_no=r.refund_no, order_id=r.order_id, amount=r.amount,
        reason=r.reason, status=r.status, channel_refund_id=r.channel_refund_id,
        created_at=r.created_at.isoformat() if r.created_at else None,
    ).model_dump()
