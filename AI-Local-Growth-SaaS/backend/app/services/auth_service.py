"""认证相关业务逻辑。"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sys_user import SysUser
from app.utils.security import verify_password


async def authenticate(db: AsyncSession, username: str, password: str) -> SysUser | None:
    """校验用户名与密码，返回用户对象或 None。

    用户不存在 / 密码错误 / 状态非 active 均返回 None。
    """
    result = await db.execute(select(SysUser).where(SysUser.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if user.status != "active":
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
