"""履约 API：预约订座 + 视频号挂载。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok, paginate
from app.core.tenant import (
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    ROLE_VERIFIER,
    TenantContext,
    get_tenant_context,
    require_role,
    tenant_filter,
)
from app.models.fulfillment import Reservation, VideoChannelBinding
from app.schemas.fulfillment import (
    ReservationCreate,
    ReservationOut,
    ReservationUpdate,
    VideoBindingCreate,
    VideoBindingOut,
)
from app.services.fulfillment import (
    bind_video_channel,
    create_reservation,
    release_expired_reservations,
    unbind_video_channel,
    update_reservation_status,
)

router = APIRouter(prefix="/fulfillment", tags=["fulfillment"])


# ---------------- 预约订座 ----------------
@router.post("/reservations")
async def create_reservation_api(
    body: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    if ctx.is_platform:
        raise BizError(ErrorCode.NO_PERMISSION, "平台不可创建预约")
    reservation = await create_reservation(db, ctx, body)
    return ok(_reservation_out(reservation))


@router.get("/reservations")
async def list_reservations_api(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
    store_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Reservation).where(Reservation.deleted_at.is_(None))
    if ctx.is_consumer:
        stmt = stmt.where(Reservation.consumer_id == ctx.user_id)
    else:
        stmt = tenant_filter(stmt, Reservation, ctx)
    if store_id is not None and ctx.is_platform:
        stmt = stmt.where(Reservation.store_id == store_id)
    total = int(await db.scalar(
        select(func.count()).select_from(stmt.subquery())
    ) or 0)
    stmt = stmt.order_by(Reservation.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([_reservation_out(r) for r in rows], total, page, page_size))


@router.patch("/reservations/{reservation_id}")
async def update_reservation_api(
    reservation_id: int, body: ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(
        require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER)
    ),
):
    reservation = await update_reservation_status(db, ctx, reservation_id, body.status)
    return ok(_reservation_out(reservation))


@router.post("/reservations/release-expired")
async def release_expired_api(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM)),
    timeout_minutes: int = Query(30, ge=1),
):
    count = await release_expired_reservations(db, timeout_minutes)
    return ok({"released": count})


# ---------------- 视频号挂载 ----------------
@router.post("/video-bindings")
async def bind_video_api(
    body: VideoBindingCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(
        require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)
    ),
):
    binding = await bind_video_channel(db, ctx, body)
    return ok(_binding_out(binding))


@router.get("/video-bindings")
async def list_video_api(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(
        require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)
    ),
    store_id: int | None = Query(None),
):
    stmt = select(VideoChannelBinding).where(VideoChannelBinding.deleted_at.is_(None))
    stmt = tenant_filter(stmt, VideoChannelBinding, ctx)
    if store_id is not None and ctx.is_platform:
        stmt = stmt.where(VideoChannelBinding.store_id == store_id)
    rows = list((await db.scalars(stmt.order_by(VideoChannelBinding.id.desc()))).all())
    return ok(paginate([_binding_out(b) for b in rows], len(rows), 1, max(len(rows), 1)))


@router.delete("/video-bindings/{binding_id}")
async def unbind_video_api(
    binding_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(
        require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)
    ),
):
    await unbind_video_channel(db, ctx, binding_id)
    return ok({"deleted": True})


# ---------------- 序列化助手 ----------------
def _reservation_out(r: Reservation) -> dict:
    return ReservationOut(
        id=r.id, merchant_id=r.merchant_id, store_id=r.store_id, consumer_id=r.consumer_id,
        order_id=r.order_id, reserve_date=r.reserve_date.isoformat() if r.reserve_date else None,
        time_slot=r.time_slot, party_size=r.party_size, table_no=r.table_no, area=r.area,
        status=r.status, remark=r.remark, created_at=_iso(r.created_at), updated_at=_iso(r.updated_at),
    ).model_dump()


def _binding_out(b: VideoChannelBinding) -> dict:
    return VideoBindingOut(
        id=b.id, merchant_id=b.merchant_id, store_id=b.store_id,
        video_account_id=b.video_account_id, poi_id=b.poi_id, poi_name=b.poi_name,
        groupbuy_link=b.groupbuy_link, status=b.status, created_at=_iso(b.created_at),
    ).model_dump()


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None
