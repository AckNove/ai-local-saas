"""核销服务：扫码/输码核销，幂等防重复核销。"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import as_utc, utc_now
from app.core.errors import BizError, ErrorCode
from app.core.tenant import TenantContext
from app.models.order import Order, VerificationCode


async def verify_code(db: AsyncSession, ctx: TenantContext, code: str) -> VerificationCode:
    """核销指定核销码。幂等防重复：UPDATE ... WHERE status=unused，rowcount=0 即已核销。

    流程：
    1. 按 code 定位（全局 UNIQUE）；不存在 → 4002 无效码。
    2. 校验归属当前商户/门店；否则 → 4002。
    3. 已 used → 4001 已核销；已 expired → 4003。
    4. 行级更新 status=used；rowcount=0（并发重复）→ 4001。
    5. 若订单全部码 used → Order→fulfilled；self_pickup 同时置 picked_up。
    """
    vc = await db.scalar(select(VerificationCode).where(VerificationCode.code == code))
    if vc is None:
        raise BizError(ErrorCode.INVALID_VERIFY_CODE)

    order = await db.scalar(select(Order).where(Order.id == vc.order_id))
    if order is None:
        raise BizError(ErrorCode.INVALID_VERIFY_CODE)

    # 跨商户/跨门店：统一返回无效码，避免泄露存在性（平台豁免，可跨商户核销）
    if not ctx.is_platform and (order.merchant_id != ctx.merchant_id or order.store_id != ctx.store_id):
        raise BizError(ErrorCode.INVALID_VERIFY_CODE)

    if vc.status == "used":
        raise BizError(ErrorCode.ALREADY_VERIFIED)
    if vc.status == "expired" or (vc.expires_at and as_utc(vc.expires_at) < utc_now()):
        raise BizError(ErrorCode.VERIFY_CODE_EXPIRED)

    # 幂等更新
    result = await db.execute(
        update(VerificationCode)
        .where(VerificationCode.id == vc.id, VerificationCode.status == "unused")
        .values(
            status="used",
            verifier_id=ctx.user_id,
            verified_at=utc_now(),
        )
    )
    if result.rowcount == 0:
        raise BizError(ErrorCode.ALREADY_VERIFIED)

    # 全部码 used → 订单完成
    total = await db.scalar(
        select(func.count()).where(VerificationCode.order_id == order.id)
    )
    used = await db.scalar(
        select(func.count()).where(
            VerificationCode.order_id == order.id,
            VerificationCode.status == "used",
        )
    )
    if total and total == used:
        order.status = "fulfilled"
        if order.fulfillment_type == "self_pickup":
            order.pickup_status = "picked_up"

    await db.commit()
    await db.refresh(vc)
    return vc


async def list_today_verifications(db: AsyncSession, ctx: TenantContext) -> list[VerificationCode]:
    """查询本门店今日核销明细（verifier 看板用）。"""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    stmt = (
        select(VerificationCode)
        .where(
            VerificationCode.merchant_id == ctx.merchant_id,
            VerificationCode.store_id == ctx.store_id,
            VerificationCode.status == "used",
            VerificationCode.verified_at >= as_utc(today_start),
        )
        .order_by(VerificationCode.verified_at.desc())
    )
    return list((await db.scalars(stmt)).all())
