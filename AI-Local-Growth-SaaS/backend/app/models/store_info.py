"""门店信息表（绑定视频号 / POI 状态）。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, SoftDeleteMixin, utc_now


class StoreInfo(Base, SoftDeleteMixin):
    """商家门店：含视频号账号与 POI 绑定状态。"""

    __tablename__ = "store_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="关联 merchant_info.id"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="门店名称")
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False, comment="位置")
    video_account: Mapped[str] = mapped_column(
        String(128), default="", nullable=False, comment="视频号账号"
    )
    poi_status: Mapped[str] = mapped_column(
        String(32), default="", nullable=False, comment="POI 绑定状态"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<StoreInfo id={self.id} merchant_id={self.merchant_id} name={self.name}>"
