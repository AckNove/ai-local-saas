"""初始化管理员与演示商家账号脚本（T04 扩展）。

创建：
- 默认管理员 admin / admin123（bcrypt 哈希）
- 演示商家账号 merchant / merchant123（role=merchant，关联首个 active 商家，便于体验商家视角）

幂等：账号已存在则跳过（merchant 账号若已存在则仅同步 merchant_id）。
用法（在 backend/ 目录）：
    python seed_admin.py
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.database import async_session_factory, init_db
from app.models.merchant_info import MerchantInfo
from app.models.sys_user import SysUser
from app.utils.security import hash_password

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
MERCHANT_USERNAME = "merchant"
MERCHANT_PASSWORD = "merchant123"


async def seed() -> None:
    # 确保表存在
    await init_db()

    async with async_session_factory() as db:
        # --- 管理员 ---
        result = await db.execute(
            select(SysUser).where(SysUser.username == ADMIN_USERNAME)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            print(f"[seed_admin] 管理员 '{ADMIN_USERNAME}' 已存在，跳过创建。")
        else:
            admin = SysUser(
                username=ADMIN_USERNAME,
                password_hash=hash_password(ADMIN_PASSWORD),
                role="admin",
                merchant_id=None,
                status="active",
            )
            db.add(admin)
            await db.commit()
            print(f"[seed_admin] 已创建管理员 '{ADMIN_USERNAME}' / 密码 '{ADMIN_PASSWORD}'。")

        # --- 演示商家账号（商家视角体验） ---
        merchant_user = await db.scalar(
            select(SysUser).where(SysUser.username == MERCHANT_USERNAME)
        )
        merchant = await db.scalar(
            select(MerchantInfo).where(MerchantInfo.status == "active").order_by(MerchantInfo.id).limit(1)
        )
        merchant_id = merchant.id if merchant else None
        if merchant_user is not None:
            if merchant_user.merchant_id != merchant_id:
                merchant_user.merchant_id = merchant_id
                await db.commit()
                print(f"[seed_admin] 商家账号 '{MERCHANT_USERNAME}' 已同步 merchant_id={merchant_id}。")
            else:
                print(f"[seed_admin] 商家账号 '{MERCHANT_USERNAME}' 已存在，跳过创建。")
        else:
            m_user = SysUser(
                username=MERCHANT_USERNAME,
                password_hash=hash_password(MERCHANT_PASSWORD),
                role="merchant",
                merchant_id=merchant_id,
                status="active",
            )
            db.add(m_user)
            await db.commit()
            print(
                f"[seed_admin] 已创建商家账号 '{MERCHANT_USERNAME}' / 密码 '{MERCHANT_PASSWORD}'"
                + (f"（关联商家 #{merchant_id}）。" if merchant_id else "（暂无商家，merchant_id 为空）。")
            )


if __name__ == "__main__":
    asyncio.run(seed())
