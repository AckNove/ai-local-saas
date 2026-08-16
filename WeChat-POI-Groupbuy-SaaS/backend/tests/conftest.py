"""测试夹具：独立 test.db + 统一响应客户端 + 演示种子数据 + JWT 助手。

所有测试使用 Mock Provider（无需任何外部凭证）。依赖覆盖 get_db 指向测试库。
"""
from __future__ import annotations

import os

# 必须在导入 app 之前设定测试库与 Mock 开关
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("WECHAT_PAY_PROVIDER", "mock")
os.environ.setdefault("MAP_POI_PROVIDER", "mock")
os.environ.setdefault("WECHAT_NOTIFY_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
import pytest_asyncio
from dataclasses import dataclass, field
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import Base
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.catalog import GroupBuyPackage, PackageStore
from app.models.tenant import (
    Merchant,
    MerchantUser,
    PlatformOperator,
    Staff,
    Store,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@dataclass
class TestCtx:
    """测试上下文：HTTP 客户端 + 种子数据 ID。"""

    client: AsyncClient
    ids: dict = field(default_factory=dict)


async def _seed(session_factory: async_sessionmaker) -> dict:
    async with session_factory() as db:
        admin = PlatformOperator(username="admin", password_hash=hash_password("admin123"))
        db.add(admin)
        await db.flush()

        merchant = Merchant(name="演示商户", status="active")
        db.add(merchant)
        await db.flush()

        merchant_user = MerchantUser(
            merchant_id=merchant.id, username="merchant",
            password_hash=hash_password("merchant123"),
        )
        db.add(merchant_user)

        store = Store(
            merchant_id=merchant.id, name="演示门店", poi_id="mock_poi_1001",
            poi_name="示例门店",
        )
        db.add(store)
        await db.flush()

        manager = Staff(
            merchant_id=merchant.id, store_id=store.id, name="店长",
            role="store_manager", username="manager",
            password_hash=hash_password("manager123"), is_active=True,
        )
        db.add(manager)
        verifier = Staff(
            merchant_id=merchant.id, store_id=store.id, name="核销员",
            role="verifier", username="verifier",
            password_hash=hash_password("verifier123"), is_active=True,
        )
        db.add(verifier)

        package = GroupBuyPackage(
            merchant_id=merchant.id, name="双人套餐", original_price=10000,
            group_price=8000, stock=100, status="published",
        )
        db.add(package)
        await db.flush()
        db.add(PackageStore(package_id=package.id, store_id=store.id))

        # 商户 B（跨租户测试用）
        merchant_b = Merchant(name="商户B", status="active")
        db.add(merchant_b)
        await db.flush()
        store_b = Store(merchant_id=merchant_b.id, name="门店B")
        db.add(store_b)
        await db.flush()
        merchant_user_b = MerchantUser(
            merchant_id=merchant_b.id, username="merchantB",
            password_hash=hash_password("merchantB123"),
        )
        db.add(merchant_user_b)

        await db.commit()
        return {
            "platform_id": admin.id,
            "merchant_id": merchant.id,
            "merchant_user_id": merchant_user.id,
            "store_id": store.id,
            "manager_id": manager.id,
            "verifier_id": verifier.id,
            "package_id": package.id,
            "merchant_b_id": merchant_b.id,
            "store_b_id": store_b.id,
            "merchant_b_user_id": merchant_user_b.id,
        }


@pytest_asyncio.fixture
async def api():
    """创建全表 + 种子数据 + 覆盖 get_db 的 HTTP 客户端。

    每个测试使用独立引擎（单连接 StaticPool），彻底隔离，避免 aiosqlite
    跨连接可见性/竞态导致的偶发 IntegrityError 与响应错乱。
    """
    engine = create_async_engine(
        TEST_DB_URL,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    ids = await _seed(SessionFactory)

    from app.core.db import get_db

    async def override_get_db():
        async with SessionFactory() as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ctx = TestCtx(client=ac, ids=ids)
        yield ctx
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------- 助手 ----------------
def make_token(user_id: int, typ: str, role: str, merchant_id=None, store_id=None) -> str:
    """直接签发 JWT（测试用）。"""
    return create_access_token(user_id, typ, role, merchant_id, store_id)


async def login(client: AsyncClient, username: str, password: str) -> str:
    """通过 web-login 获取 token。"""
    resp = await client.post(
        "/api/v1/auth/web-login", json={"username": username, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
