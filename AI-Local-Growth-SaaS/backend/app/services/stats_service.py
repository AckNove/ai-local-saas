"""数据统计服务：聚合商家 / 门店 / 种草卡与 seed_event。"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seed_card import SeedCard
from app.models.seed_event import SeedEvent
from app.models.store_info import StoreInfo
from app.models.merchant_info import MerchantInfo
from app.models.sys_user import SysUser


def _scope(current_user: SysUser, requested: int | None) -> int | None:
    """确定统计作用域 merchant_id。

    merchant 角色强制只看自己；admin 若不传 merchant_id 则看全部。
    """
    if current_user.role == "merchant":
        return current_user.merchant_id
    return requested


def _event_base(scope: int | None):
    """构建带作用域的 seed_event 查询（join 到 active 种草卡）。"""
    stmt = select(SeedEvent).join(
        SeedCard, SeedEvent.card_id == SeedCard.id
    ).where(SeedCard.status == "active")
    if scope is not None:
        stmt = stmt.where(SeedCard.merchant_id == scope)
    return stmt


async def overview(
    db: AsyncSession, current_user: SysUser, requested_merchant_id: int | None = None
) -> dict:
    """统计概览：商家数 / 门店数 / 种草卡数 / 各类事件数 / 近期事件。"""
    scope = _scope(current_user, requested_merchant_id)

    # 商家数
    m_stmt = select(func.count()).select_from(MerchantInfo).where(
        MerchantInfo.status != "deleted"
    )
    if scope is not None:
        m_stmt = m_stmt.where(MerchantInfo.id == scope)
    merchant_count = (await db.execute(m_stmt)).scalar_one()

    # 门店数
    s_stmt = select(func.count()).select_from(StoreInfo).where(
        StoreInfo.status != "deleted"
    )
    if scope is not None:
        s_stmt = s_stmt.where(StoreInfo.merchant_id == scope)
    store_count = (await db.execute(s_stmt)).scalar_one()

    # 种草卡数
    c_stmt = select(func.count()).select_from(SeedCard).where(
        SeedCard.status == "active"
    )
    if scope is not None:
        c_stmt = c_stmt.where(SeedCard.merchant_id == scope)
    card_count = (await db.execute(c_stmt)).scalar_one()

    # 事件计数
    scan_total = share_total = click_total = comment_total = 0
    for etype in ("scan", "click", "share", "comment"):
        stmt = select(func.count()).select_from(
            _event_base(scope).where(SeedEvent.event_type == etype).subquery()
        )
        value = (await db.execute(stmt)).scalar_one()
        if etype == "scan":
            scan_total = value
        elif etype == "click":
            click_total = value
        elif etype == "share":
            share_total = value
        else:
            comment_total = value

    # 近期事件（最近 20 条）
    recent_rows = (
        await db.execute(
            _event_base(scope)
            .order_by(SeedEvent.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    recent_events = [
        {
            "card_id": e.card_id,
            "event_type": e.event_type,
            "created_at": e.created_at,
        }
        for e in recent_rows
    ]

    # 近 7 天趋势（按天聚合 scan + click 两类核心事件）
    trend = await _daily_trend(db, scope)

    return {
        "merchant_count": merchant_count,
        "store_count": store_count,
        "card_count": card_count,
        "scan_total": scan_total,
        "click_total": click_total,
        "share_total": share_total,
        "comment_total": comment_total,
        "recent_events": recent_events,
        "trend": trend,
    }


async def _daily_trend(db: AsyncSession, scope: int | None, days: int = 7) -> list[dict]:
    """近 N 天扫码/点击趋势（按日期聚合，返回按日期升序的序列）。"""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # 取近 N 天事件，按天分组
    rows = (
        await db.execute(
            _event_base(scope)
            .where(SeedEvent.created_at >= start)
            .where(SeedEvent.event_type.in_(["scan", "click"]))
        )
    ).scalars().all()

    # 初始化日期桶（从 start 到今天）
    buckets: dict[str, dict] = {}
    for i in range(days):
        d = (start + timedelta(days=i)).date().isoformat()
        buckets[d] = {"date": d, "scan": 0, "click": 0}

    for e in rows:
        dt = e.created_at
        # SQLite 回读可能丢失时区，统一按 UTC 处理（与 utc_now 一致）
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        d = dt.date().isoformat()
        if d in buckets:
            if e.event_type == "scan":
                buckets[d]["scan"] += 1
            elif e.event_type == "click":
                buckets[d]["click"] += 1

    return [buckets[k] for k in sorted(buckets.keys())]
