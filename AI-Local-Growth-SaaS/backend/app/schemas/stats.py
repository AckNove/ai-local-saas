"""统计接口 Schema。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RecentEvent(BaseModel):
    card_id: int
    event_type: str
    created_at: datetime


class TrendPoint(BaseModel):
    date: str
    scan: int = 0
    click: int = 0


class StatsOverviewOut(BaseModel):
    merchant_count: int = 0
    store_count: int = 0
    card_count: int = 0
    scan_total: int = 0
    click_total: int = 0
    share_total: int = 0
    comment_total: int = 0
    recent_events: list[RecentEvent] = Field(default_factory=list)
    trend: list[TrendPoint] = Field(default_factory=list)
