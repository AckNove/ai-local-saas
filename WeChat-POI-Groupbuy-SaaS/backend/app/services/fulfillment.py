"""履约服务：外卖自提状态机、预约订座时段库存、视频号挂载。"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import as_utc, utc_now
from app.core.errors import BizError, ErrorCode
from app.core.tenant import TenantContext
from app.models.fulfillment import Reservation, VideoChannelBinding
from app.models.order import Order
from app.models.tenant import Store
from app.schemas.fulfillment import ReservationCreate, VideoBindingCreate
from app.services.map.factory import get_map_provider
from app.services.notification.factory import get_notification_provider


# ---------------- 自提状态机 ----------------
async def update_pickup_status(
    db: AsyncSession, ctx: TenantContext, order_no: str, new_status: str
) -> Order:
    """商家更新自提备餐状态：preparing -> ready -> picked_up。

    ready 时调用 NotificationProvider 通知消费者（Mock 恒成功）。
    """
    if new_status not in ("preparing", "ready", "picked_up"):
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "非法的备餐状态")

    order = await db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None:
        raise BizError(ErrorCode.ORDER_NOT_FOUND)
    if order.merchant_id != ctx.merchant_id or order.store_id != ctx.store_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    if order.fulfillment_type != "self_pickup":
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "非自提订单")
    if order.status not in ("paid", "fulfilled"):
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "订单未支付")

    current = order.pickup_status or "preparing"
    if current == "picked_up":
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "已取餐，状态终态")

    order.pickup_status = new_status

    if new_status == "ready" and current == "preparing":
        provider = get_notification_provider()
        await provider.notify(
            "ready",
            {"order_no": order.order_no, "store_id": order.store_id},
        )

    await db.commit()
    await db.refresh(order)
    return order


# ---------------- 预约订座 ----------------
def _parse_reserve_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise BizError(ErrorCode.RESERVATION_STATUS_INVALID, "预约日期格式应为 YYYY-MM-DD") from exc


async def _occupied_count(
    db: AsyncSession, store_id: int, reserve_date: date, time_slot: str
) -> int:
    """统计该时段占用（pending/confirmed 视为占用）。"""
    return int(
        await db.scalar(
            select(func.count()).where(
                Reservation.store_id == store_id,
                Reservation.reserve_date == reserve_date,
                Reservation.time_slot == time_slot,
                Reservation.status.in_(["pending", "confirmed"]),
                Reservation.deleted_at.is_(None),
            )
        )
        or 0
    )


async def create_reservation(
    db: AsyncSession, ctx: TenantContext, data: ReservationCreate
) -> Reservation:
    """创建预约并占用时段库存；满额返回 6001。"""
    store = await db.scalar(select(Store).where(Store.id == data.store_id))
    if store is None or store.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "门店不存在")
    # 消费者下单为公开行为（无 merchant_id），仅对商户/员工校验归属同一商户
    if (ctx.is_merchant or ctx.is_staff) and store.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)

    reserve_date = _parse_reserve_date(data.reserve_date)
    occupied = await _occupied_count(db, store.id, reserve_date, data.time_slot)
    if occupied >= settings.SLOT_CAPACITY:
        raise BizError(ErrorCode.SLOT_FULL)

    reservation = Reservation(
        merchant_id=store.merchant_id,
        store_id=store.id,
        consumer_id=ctx.user_id,
        reserve_date=reserve_date,
        time_slot=data.time_slot,
        party_size=data.party_size,
        table_no=data.table_no,
        area=data.area,
        remark=data.remark,
        status="pending",
        order_id=None,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation


async def update_reservation_status(
    db: AsyncSession, ctx: TenantContext, reservation_id: int, new_status: str
) -> Reservation:
    """预约状态流转：confirmed / arrived / cancelled。

    非法流转返回 6003；cancelled 释放时段库存（从占用计数移除）。
    """
    allowed = {"confirmed", "arrived", "cancelled"}
    if new_status not in allowed:
        raise BizError(ErrorCode.RESERVATION_STATUS_INVALID)

    reservation = await db.scalar(select(Reservation).where(Reservation.id == reservation_id))
    if reservation is None or reservation.deleted_at is not None:
        raise BizError(ErrorCode.RESERVATION_NOT_FOUND)
    if not ctx.is_platform and reservation.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)

    valid_transitions = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"arrived", "cancelled"},
        "arrived": set(),
        "cancelled": set(),
        "released": set(),
    }
    if new_status not in valid_transitions.get(reservation.status, set()):
        raise BizError(ErrorCode.RESERVATION_STATUS_INVALID, "预约状态非法流转")

    reservation.status = new_status
    await db.commit()
    await db.refresh(reservation)
    return reservation


async def release_expired_reservations(
    db: AsyncSession, timeout_minutes: int = 30
) -> int:
    """将超时未确认的 pending 预约回收为 released（释放时段库存）。"""
    threshold = utc_now() - timedelta(minutes=timeout_minutes)
    stmt = select(Reservation).where(
        Reservation.status == "pending",
        as_utc(Reservation.created_at) < threshold,
        Reservation.deleted_at.is_(None),
    )
    expired = list((await db.scalars(stmt)).all())
    for r in expired:
        r.status = "released"
    if expired:
        await db.commit()
    return len(expired)


# ---------------- 视频号挂载 ----------------
async def bind_video_channel(
    db: AsyncSession, ctx: TenantContext, data: VideoBindingCreate
) -> VideoChannelBinding:
    """绑定视频号 + POI（调 MapProvider 解析），生成团购落地链接。"""
    store = await db.scalar(select(Store).where(Store.id == data.store_id))
    if store is None or store.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "门店不存在")
    if not ctx.is_platform and store.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)

    map_provider = get_map_provider()
    poi = await map_provider.resolve_poi(data.poi_id)

    binding = VideoChannelBinding(
        merchant_id=store.merchant_id,
        store_id=store.id,
        video_account_id=data.video_account_id,
        poi_id=poi.get("poi_id") or data.poi_id,
        poi_name=poi.get("poi_name"),
        status="active",
    )
    db.add(binding)
    await db.flush()
    binding.groupbuy_link = (
        f"https://weixin.qq.com/groupbuy?binding_id={binding.id}"
    )
    await db.commit()
    await db.refresh(binding)
    return binding


async def unbind_video_channel(
    db: AsyncSession, ctx: TenantContext, binding_id: int
) -> None:
    """解绑视频号（软删除）。"""
    binding = await db.scalar(
        select(VideoChannelBinding).where(VideoChannelBinding.id == binding_id)
    )
    if binding is None or binding.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "绑定不存在")
    if not ctx.is_platform and binding.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    binding.soft_delete()
    await db.commit()
