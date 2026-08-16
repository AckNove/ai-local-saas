"""异步数据库引擎、会话工厂、声明式基类与软删除混入。

引擎在导入时根据 settings.DATABASE_URL 创建。测试可通过覆盖 get_db 依赖
或重建引擎来使用临时库，无需改动业务代码。
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings


def utc_now() -> datetime:
    """返回带时区的当前 UTC 时间，用作默认值与入库值。"""
    return datetime.now(timezone.utc)


def as_utc(dt: datetime | None) -> datetime | None:
    """将 SQLite 读回的 naive 时间统一视为 UTC 并转为 aware，便于与 utc_now() 比较。

    SQLite 的 DateTime(timezone=True) 在回读时会丢失时区信息变成 naive，
    而 utc_now() 返回 aware；比较前用本函数把 naive 值补齐为 aware（UTC），
    避免「can't compare offset-naive and offset-aware」错误。
    """
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""


class SoftDeleteMixin:
    """软删除混入：提供 deleted_at 字段与 soft_delete() 方法。

    查询默认过滤 deleted_at IS NULL 的记录。禁止对核心业务表执行物理 DELETE。
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="软删除时间，NULL=未删除",
    )

    def soft_delete(self) -> None:
        """软删除：仅置 deleted_at，不物理删除。"""
        self.deleted_at = utc_now()


def make_engine(database_url: str):
    """创建异步引擎。SQLite 关闭单线程检查以兼容异步并发。"""
    connect_args: dict = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )


engine = make_engine(settings.DATABASE_URL)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：为每个请求提供一个异步会话。"""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """创建所有表（幂等）。保留为兜底，生产以 Alembic 迁移为准。"""
    from app import models  # noqa: F401  确保模型注册到 Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "Base",
    "SoftDeleteMixin",
    "AsyncSession",
    "DeclarativeBase",
    "engine",
    "async_session_factory",
    "get_db",
    "init_db",
    "make_engine",
    "utc_now",
]
