"""种子数据：平台运营 + 演示商户 + 门店 + 商户主 + 店长 + 核销员。

运行：cd backend && python scripts/seed.py
（请先 `python -m alembic upgrade head` 建表）
"""
from __future__ import annotations

import asyncio
import os
import sys

# 确保 backend 在 sys.path，便于直接运行脚本
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.core.db import Base, async_session_factory, engine, make_engine, utc_now
from app.core.security import hash_password
from app.models.tenant import (
    Consumer,
    Merchant,
    MerchantUser,
    PlatformOperator,
    Staff,
    Store,
)
from app.models.catalog import GroupBuyPackage, PackageStore


async def seed() -> None:
    # 幂等：已存在平台运营则跳过
    async with async_session_factory() as db:
        existing = await db.scalar(
            select(PlatformOperator).where(PlatformOperator.username == "admin")
        )
        if existing is not None:
            print("种子数据已存在，跳过。")
            return

        admin = PlatformOperator(username="admin", password_hash=hash_password("admin123"))
        db.add(admin)

        merchant = Merchant(name="演示商户", contact_phone="13800000000", status="active")
        db.add(merchant)
        await db.flush()

        merchant_user = MerchantUser(
            merchant_id=merchant.id, username="merchant",
            password_hash=hash_password("merchant123"),
        )
        db.add(merchant_user)

        store = Store(
            merchant_id=merchant.id, name="演示门店（中心店）",
            address="北京市朝阳区示例路 1 号", phone="13800000000",
            business_hours="09:00-22:00", poi_id="mock_poi_1001",
            poi_name="示例门店（Mock POI）", lng=116.397428, lat=39.90923,
        )
        db.add(store)
        await db.flush()

        manager = Staff(
            merchant_id=merchant.id, store_id=store.id, name="王店长",
            role="store_manager", username="manager",
            password_hash=hash_password("manager123"), is_active=True,
        )
        db.add(manager)

        verifier = Staff(
            merchant_id=merchant.id, store_id=store.id, name="李核销",
            role="verifier", username="verifier",
            password_hash=hash_password("verifier123"), is_active=True,
        )
        db.add(verifier)

        package = GroupBuyPackage(
            merchant_id=merchant.id, name="双人套餐", description="超值双人餐",
            original_price=10000, group_price=8000, stock=100, sold_count=0,
            status="published", images_json='["https://example.com/p1.jpg"]',
        )
        db.add(package)
        await db.flush()
        db.add(PackageStore(package_id=package.id, store_id=store.id))

        await db.commit()
        print("种子数据创建成功：")
        print("  平台运营  admin / admin123")
        print("  商户主    merchant / merchant123")
        print("  店长      manager / manager123")
        print("  核销员    verifier / verifier123")
        print(f"  商户ID={merchant.id} 门店ID={store.id} 套餐ID={package.id}")


async def main() -> None:
    # 确保表存在（兜底；生产以 alembic 为准）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
