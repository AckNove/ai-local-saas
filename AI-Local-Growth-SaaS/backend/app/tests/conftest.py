"""pytest 公共夹具：独立临时 SQLite 库 + 异步测试 client + 默认管理员 token。

设计要点：
- 每个测试使用各自的临时 SQLite 文件，避免污染真实 app.db。
- 通过覆盖 app.database 的全局 engine / async_session_factory 与 get_db 依赖，
  使业务代码无需改动即可跑在测试库上。
- 显式将 backend/ 加入 sys.path，保证无论从何处运行 pytest 都能 import main / config / app。
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# 确保 backend/ 在 sys.path，保证 `import main` / `from config import` 可用
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# 测试环境配置（仅设置默认值，不覆盖已显式指定的环境变量）
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "test-secret-key-pytest-0123456789")
os.environ.setdefault("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.database import Base  # noqa: F401  (确保 Base 可用)
import app.database as database_module
from app import models  # noqa: F401  (注册所有 ORM 模型，建表所需)
from main import app
from app.models.sys_user import SysUser
from app.utils.security import create_access_token, hash_password

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@pytest_asyncio.fixture
async def client():
    """每个测试使用独立临时 SQLite 库，并覆盖 get_db 依赖。"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    url = f"sqlite+aiosqlite:///{tmp.name}"
    engine = create_async_engine(url, future=True, connect_args={"check_same_thread": False})
    factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    # 覆盖全局引擎与会话工厂（属性赋值，调用时解析为最新值）
    database_module.engine = engine
    database_module.async_session_factory = factory
    await database_module.init_db()

    async def _override_get_db() -> AsyncSession:
        async with factory() as session:
            yield session

    app.dependency_overrides[database_module.get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest_asyncio.fixture
async def admin_user(client):
    """在测试库中插入默认管理员。"""
    async with database_module.async_session_factory() as db:
        user = SysUser(
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
            merchant_id=None,
            status="active",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user):
    """默认管理员的 JWT。"""
    return create_access_token(admin_user.id, admin_user.role, admin_user.merchant_id)


@pytest_asyncio.fixture
async def register_user(client):
    """工厂：在测试库中插入一个用户并返回对象。"""

    async def _make(
        username: str,
        password: str = "secret123",
        role: str = "merchant",
        merchant_id: int | None = None,
        status: str = "active",
    ) -> SysUser:
        async with database_module.async_session_factory() as db:
            user = SysUser(
                username=username,
                password_hash=hash_password(password),
                role=role,
                merchant_id=merchant_id,
                status=status,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    return _make


@pytest.fixture
def make_token():
    """工厂：由 SysUser 对象签发 JWT。"""

    def _make(user: SysUser) -> str:
        return create_access_token(user.id, user.role, user.merchant_id)

    return _make
