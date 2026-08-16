"""经营指标聚合服务（无新表，基于既有 Order/VerificationCode/Refund/Reservation）。

指标口径（与架构第 3 节一致）：
- 销量      = 已支付订单对应 OrderItem.quantity 之和
- 核销率    = 已核销核销码数 / 需核销的已支付订单数（dine_in/self_pickup）
- GMV       = 已支付订单 total_amount 之和（不含 refunded）
- 自提转化  = 自提已支付订单 / 已支付订单
- 订座转化  = (arrived+confirmed) 预约 / 总预约
- 内容引流  = source=video_channel 订单 / 总已支付订单
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import as_utc

from app.models.fulfillment import Reservation
from app.models.order import Order, OrderItem, VerificationCode

_PAID_STATUSES = ("paid", "fulfilled", "refunded")
_NEED_VERIFY_TYPES = ("dine_in", "self_pickup")


def _date_filters(model, date_from: datetime | None, date_to: datetime | None):
    conds = []
    if date_from is not None:
        conds.append(as_utc(model.created_at) >= date_from)
    if date_to is not None:
        conds.append(as_utc(model.created_at) <= date_to)
    return conds


async def compute_metrics(
    db: AsyncSession,
    merchant_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    """聚合经营指标；merchant_id=None 表示平台汇总（跨商户）。"""
    order_conds = []
    if merchant_id is not None:
        order_conds.append(Order.merchant_id == merchant_id)
    order_conds += _date_filters(Order, date_from, date_to)

    # 销量
    sales = await db.scalar(
        select(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status.in_(_PAID_STATUSES), *order_conds)
    )
    # GMV
    gmv = await db.scalar(
        select(func.coalesce(func.sum(Order.total_amount), 0)).where(
            Order.status.in_(("paid", "fulfilled")), *order_conds
        )
    )
    # 已支付订单总数
    paid_total = int(
        await db.scalar(
            select(func.count()).where(Order.status.in_(_PAID_STATUSES), *order_conds)
        )
        or 0
    )
    # 需核销的已支付订单数
    need_verify_total = int(
        await db.scalar(
            select(func.count()).where(
                Order.status.in_(_PAID_STATUSES),
                Order.fulfillment_type.in_(_NEED_VERIFY_TYPES),
                *order_conds,
            )
        )
        or 0
    )
    # 已核销核销码数
    vc_conds = []
    if merchant_id is not None:
        vc_conds.append(VerificationCode.merchant_id == merchant_id)
    verified = int(
        await db.scalar(
            select(func.count()).where(
                VerificationCode.status == "used", *vc_conds
            )
        )
        or 0
    )
    # 自提已支付订单数
    self_pickup_total = int(
        await db.scalar(
            select(func.count()).where(
                Order.status.in_(_PAID_STATUSES),
                Order.fulfillment_type == "self_pickup",
                *order_conds,
            )
        )
        or 0
    )
    # 内容引流订单数
    video_total = int(
        await db.scalar(
            select(func.count()).where(
                Order.status.in_(_PAID_STATUSES),
                Order.source == "video_channel",
                *order_conds,
            )
        )
        or 0
    )

    verify_rate = (verified / need_verify_total) if need_verify_total else 0.0
    self_pickup_rate = (self_pickup_total / paid_total) if paid_total else 0.0
    video_rate = (video_total / paid_total) if paid_total else 0.0

    # 预约订座
    res_conds = []
    if merchant_id is not None:
        res_conds.append(Reservation.merchant_id == merchant_id)
    res_conds += _date_filters(Reservation, date_from, date_to)
    res_total = int(
        await db.scalar(select(func.count()).where(*res_conds)) or 0
    )
    res_active = int(
        await db.scalar(
            select(func.count()).where(
                Reservation.status.in_(("arrived", "confirmed")), *res_conds
            )
        )
        or 0
    )
    reservation_rate = (res_active / res_total) if res_total else 0.0

    return {
        "sales_volume": int(sales or 0),
        "gmv": int(gmv or 0),
        "paid_orders": paid_total,
        "verified_count": verified,
        "verify_rate": round(verify_rate, 4),
        "self_pickup_rate": round(self_pickup_rate, 4),
        "video_channel_rate": round(video_rate, 4),
        "reservation_total": res_total,
        "reservation_rate": round(reservation_rate, 4),
    }
