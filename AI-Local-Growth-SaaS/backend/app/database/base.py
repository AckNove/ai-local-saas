"""声明式基类与软删除混入。

软删除统一通过 `status` 字段表达生命周期：
- active  : 正常
- disabled: 被禁用（仍可见，便于恢复）
- deleted : 软删除（列表默认排除）

禁止对业务表执行物理 DELETE，统一调用 `soft_delete()`。
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""


class SoftDeleteMixin:
    """软删除混入：提供 status 字段与 soft_delete() 方法。

    列表查询默认排除 status == 'deleted' 的记录，保留 active 与 disabled
    以便管理员在后台查看并恢复被禁用的记录。
    """

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active/disabled/deleted",
    )

    def soft_delete(self) -> None:
        """软删除：仅置状态为 deleted，不物理删除。"""
        self.status = "deleted"


def utc_now() -> datetime:
    """返回带时区的当前 UTC 时间，用作默认值。"""
    return datetime.now(timezone.utc)
