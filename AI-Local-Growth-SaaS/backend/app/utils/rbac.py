"""RBAC 依赖：解析当前用户、按角色鉴权。

鉴权统一在依赖注入层完成，禁止在各 handler 内重复判断。
- get_current_user：解析 Bearer Token，返回 SysUser（或 401）。
- require_role(*roles)：返回依赖工厂，校验角色（或 403）。
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sys_user import SysUser
from app.utils.security import decode_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> SysUser:
    """从 Authorization 头解析并加载当前用户。

    无令牌 / 令牌无效 / 用户不存在或不可用 → 抛出 401（由全局异常处理统一封装）。
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未认证")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    user_id = int(payload.get("sub", 0))
    result = await db.execute(select(SysUser).where(SysUser.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or user.status != "active":
        raise HTTPException(status_code=401, detail="用户不可用")
    return user


def require_role(*roles: str) -> Callable[..., Awaitable[SysUser]]:
    """角色依赖工厂：当前用户角色不在允许列表内 → 403。"""

    async def _checker(current_user: SysUser = Depends(get_current_user)) -> SysUser:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="无权限")
        return current_user

    return _checker
