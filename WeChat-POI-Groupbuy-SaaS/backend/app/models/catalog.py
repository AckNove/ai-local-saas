"""团购套餐模型：GroupBuyPackage 与适用门店关联表 PackageStore。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, SoftDeleteMixin, utc_now


class GroupBuyPackage(Base, SoftDeleteMixin):
    """团购套餐：金额字段一律 INT（分）。"""

    __tablename__ = "group_buy_package"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="套餐名")
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    original_price: Mapped[int] = mapped_column(Integer, nullable=False, comment="原价（分）")
    group_price: Mapped[int] = mapped_column(Integer, nullable=False, comment="团购价（分）")
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总库存")
    sold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="已售")
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False,
        comment="draft/published/off_shelf/expired",
    )
    images_json: Mapped[str | None] = mapped_column(String(2048), nullable=True, comment="图文 JSON")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class PackageStore(Base):
    """套餐-门店适用关联表（多对多）。无软删除（关联实体）。"""

    __tablename__ = "package_store"
    __table_args__ = (
        UniqueConstraint("package_id", "store_id", name="uq_package_store"),
    )

    package_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("group_buy_package.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
    )
