"""种草卡互动事件表（只追加，不删除）。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, utc_now


class SeedEvent(Base):
    """消费者在 H5 落地页的互动事件：scan/click/share/comment。

    审计类表：只追加，禁止删除，保障统计可追溯。
    """

    __tablename__ = "seed_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="关联 seed_card.id"
    )
    event_type: Mapped[str] = mapped_column(
        String(16), nullable=False, index=True, comment="scan/click/share/comment"
    )
    device: Mapped[str] = mapped_column(String(32), default="", nullable=False, comment="设备类型")
    referer: Mapped[str] = mapped_column(String(512), default="", nullable=False, comment="来源页")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SeedEvent id={self.id} card_id={self.card_id} type={self.event_type}>"
