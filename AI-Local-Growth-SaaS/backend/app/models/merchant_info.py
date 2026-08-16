"""商家信息表。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, SoftDeleteMixin, utc_now


class MerchantInfo(Base, SoftDeleteMixin):
    """入驻商家。"""

    __tablename__ = "merchant_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="商家名称")
    industry: Mapped[str] = mapped_column(String(64), default="", nullable=False, comment="行业")
    address: Mapped[str] = mapped_column(String(255), default="", nullable=False, comment="地址")
    contact: Mapped[str] = mapped_column(String(64), default="", nullable=False, comment="联系人")
    phone: Mapped[str] = mapped_column(String(32), default="", nullable=False, comment="联系电话")
    package: Mapped[str] = mapped_column(String(64), default="", nullable=False, comment="套餐")
    expire_time: Mapped[str] = mapped_column(
        String(32), default="", nullable=False, comment="到期时间（字符串，避免时区方言差异）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MerchantInfo id={self.id} name={self.name}>"
