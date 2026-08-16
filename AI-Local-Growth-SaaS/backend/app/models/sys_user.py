"""系统用户表：管理员 / 商家 / 代理（代理仅预留）。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, SoftDeleteMixin, utc_now


class SysUser(Base, SoftDeleteMixin):
    """系统用户。

    role 枚举：admin（管理员）/ merchant（商家）/ agent（代理，仅预留）。
    merchant 角色的 merchant_id 指向其所属商家。
    """

    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="登录名"
    )
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="bcrypt 哈希")
    role: Mapped[str] = mapped_column(
        String(20), default="merchant", nullable=False, comment="admin/merchant/agent"
    )
    merchant_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True, comment="商家角色关联的 merchant_info.id"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SysUser id={self.id} username={self.username} role={self.role}>"
