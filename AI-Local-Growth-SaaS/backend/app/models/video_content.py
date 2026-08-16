"""视频内容表（AI 内容生成的落库）。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, SoftDeleteMixin, utc_now


class VideoContent(Base, SoftDeleteMixin):
    """AI 生成的视频脚本 / 文案等草稿内容。"""

    __tablename__ = "video_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="关联 merchant_info.id（0 表示平台/管理员）"
    )
    title: Mapped[str] = mapped_column(String(255), default="", nullable=False, comment="标题")
    url: Mapped[str] = mapped_column(String(512), default="", nullable=False, comment="关联链接")
    category: Mapped[str] = mapped_column(
        String(32), default="script", nullable=False, comment="类型：script/copy 等"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VideoContent id={self.id} category={self.category}>"
