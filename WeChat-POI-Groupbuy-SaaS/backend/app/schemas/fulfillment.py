"""履约 Schema：预约订座 / 视频号挂载。"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------- Reservation ----------------
class ReservationCreate(BaseModel):
    store_id: int = Field(..., gt=0)
    reserve_date: str = Field(..., description="预约日期 YYYY-MM-DD")
    time_slot: str = Field(..., description="时段，如 18:00-19:00")
    party_size: int = Field(default=1, ge=1, le=50)
    table_no: str | None = None
    area: str | None = None
    remark: str | None = None
    channel_binding_id: int | None = None


class ReservationUpdate(BaseModel):
    """预约状态流转：confirmed / arrived / cancelled。"""

    status: str


class ReservationOut(BaseModel):
    id: int
    merchant_id: int
    store_id: int
    consumer_id: int
    order_id: int | None = None
    reserve_date: str
    time_slot: str
    party_size: int
    table_no: str | None = None
    area: str | None = None
    status: str
    remark: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ---------------- VideoChannelBinding ----------------
class VideoBindingCreate(BaseModel):
    store_id: int = Field(..., gt=0)
    video_account_id: str = Field(..., min_length=1)
    poi_id: str | None = None


class VideoBindingOut(BaseModel):
    id: int
    merchant_id: int
    store_id: int
    video_account_id: str
    poi_id: str | None = None
    poi_name: str | None = None
    groupbuy_link: str | None = None
    status: str
    created_at: str | None = None
