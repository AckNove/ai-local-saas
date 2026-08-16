"""履约模型：Reservation（预约订座）与 VideoChannelBinding（视频号挂载）。"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, SoftDeleteMixin, utc_now


class Reservation(Base, SoftDeleteMixin):
    """预约订座：store_id + reserve_date + time_slot 占用门店时段库存。

    状态机：pending -> confirmed -> arrived / cancelled / released。
    注：扩展 order_id（可空）用于与付费订单关联，便于归因与履约联动。
    """

    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    consumer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("consumer.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    reserve_date: Mapped[date] = mapped_column(Date, nullable=False, comment="预约日期")
    time_slot: Mapped[str] = mapped_column(String(32), nullable=False, comment="时段，如 18:00-19:00")
    party_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False, comment="人数")
    table_no: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="桌位号")
    area: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="区域")
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False,
        comment="pending/confirmed/arrived/cancelled/released",
    )
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class VideoChannelBinding(Base, SoftDeleteMixin):
    """视频号挂载：绑定视频号 + POI + 团购链接，用于内容引流归因。"""

    __tablename__ = "video_channel_binding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    video_account_id: Mapped[str] = mapped_column(String(128), nullable=False, comment="视频号账号 ID")
    poi_id: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="地图 POI ID")
    poi_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="POI 名称")
    groupbuy_link: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="团购落地链接")
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False, comment="active/inactive"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
