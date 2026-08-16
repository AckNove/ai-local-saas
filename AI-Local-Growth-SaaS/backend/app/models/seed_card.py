"""种草卡表：NFC / 二维码入口，含跳转目标与二维码。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, SoftDeleteMixin, utc_now


class SeedCard(Base, SoftDeleteMixin):
    """种草卡（消费入口）。

    type: NFC / 二维码（二维码为主路径，NFC 仅建数据模型）
    target_type: video（视频号）/ private（私域）/ custom（自定义）
    slug: 唯一短码，落地页 /c/{slug}
    qr_code: segno 生成的二维码 data URI（PNG base64）
    """

    __tablename__ = "seed_card"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="关联 merchant_info.id"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="卡片名称")
    slug: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, comment="唯一短码"
    )
    type: Mapped[str] = mapped_column(
        String(16), default="二维码", nullable=False, comment="NFC/二维码"
    )
    target_type: Mapped[str] = mapped_column(
        String(16), default="video", nullable=False, comment="video/private/custom"
    )
    target_url: Mapped[str] = mapped_column(
        String(512), default="", nullable=False, comment="跳转目标 URL"
    )
    nfc_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="NFC 标签 ID（写卡由外部工具完成）"
    )
    qr_code: Mapped[str | None] = mapped_column(
        String(4096), nullable=True, comment="二维码 data URI（PNG base64）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SeedCard id={self.id} slug={self.slug} name={self.name}>"
