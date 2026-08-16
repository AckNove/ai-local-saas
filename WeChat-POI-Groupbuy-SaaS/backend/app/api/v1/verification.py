"""核销 API：扫码/输码核销（幂等防重）+ 今日核销明细。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.responses import ok
from app.core.tenant import (
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    ROLE_VERIFIER,
    require_role,
)
from app.models.order import Order, VerificationCode
from app.schemas.order import VerifyIn
from app.services.verification import list_today_verifications, verify_code

router = APIRouter(prefix="/verify", tags=["verification"])


@router.post("")
async def verify_api(
    body: VerifyIn,
    db: AsyncSession = Depends(get_db),
    ctx=Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER)),
):
    vc = await verify_code(db, ctx, body.code)
    order = await db.scalar(select(Order).where(Order.id == vc.order_id))
    return ok(
        {
            "verified": True,
            "code": vc.code,
            "order_no": order.order_no if order else None,
            "fulfillment_type": order.fulfillment_type if order else None,
            "verified_at": vc.verified_at.isoformat() if vc.verified_at else None,
        }
    )


@router.get("/today")
async def today_api(
    db: AsyncSession = Depends(get_db),
    ctx=Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER)),
):
    rows = await list_today_verifications(db, ctx)
    data = [
        {
            "code": v.code,
            "order_id": v.order_id,
            "verified_at": v.verified_at.isoformat() if v.verified_at else None,
        }
        for v in rows
    ]
    return ok({"list": data, "total": len(data)})
