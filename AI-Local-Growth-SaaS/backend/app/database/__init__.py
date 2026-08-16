"""异步数据库引擎、会话工厂与 FastAPI 依赖。

引擎在导入时根据 config.DATABASE_URL 创建。测试可通过覆盖 get_db 依赖
或重建引擎来使用临时库，无需改动业务代码。
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL
from app.database.base import Base


def make_engine(database_url: str = DATABASE_URL):
    """创建异步引擎。

    对 SQLite 关闭 SQLite 的写者锁检查，避免异步并发下的告警。
    """
    connect_args: dict = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )


engine = make_engine()

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
    """创建所有表（幂等）。在应用启动时调用。"""
    # 导入模型以确保元数据被注册
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "Base",
    "AsyncSession",
    "engine",
    "async_session_factory",
    "get_db",
    "init_db",
    "make_engine",
    "DeclarativeBase",
]
