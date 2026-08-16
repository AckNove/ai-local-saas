"""多租户上下文：TenantContext、JWT 解析依赖、角色守卫、查询过滤助手。

设计要点（架构第 7 节）：
- JWT 载荷注入 TenantContext，查询层通过 tenant_filter() 自动加 merchant_id / store_id 过滤，
  禁止业务代码手写 if 判断租户。
- 5 角色 RBAC：platform_operator / merchant_owner / store_manager / verifier / consumer。
- 4 类主体（typ）：platform（跨商户）/ merchant（限 merchant_id）/
  staff（限 merchant_id + store_id）/ consumer（限自身 sub）。
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Select

from app.core.errors import BizError, ErrorCode
from app.core.security import decode_token

# 角色常量
ROLE_PLATFORM = "platform_operator"
ROLE_MERCHANT = "merchant_owner"
ROLE_STORE_MANAGER = "store_manager"
ROLE_VERIFIER = "verifier"
ROLE_CONSUMER = "consumer"

# 主体类型常量
TYP_PLATFORM = "platform"
TYP_MERCHANT = "merchant"
TYP_STAFF = "staff"
TYP_CONSUMER = "consumer"

# 允许登录的账号体系（平台/商户/员工走 web-login；消费者走 wx-login）
STAFF_ROLES = {ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER}

_bearer = HTTPBearer(auto_error=False)


@dataclass
class TenantContext:
    """当前请求的身份与租户上下文。"""

    user_id: int
    typ: str
    role: str
    merchant_id: int | None = None
    store_id: int | None = None

    @property
    def is_platform(self) -> bool:
        return self.typ == TYP_PLATFORM

    @property
    def is_consumer(self) -> bool:
        return self.typ == TYP_CONSUMER

    @property
    def is_staff(self) -> bool:
        return self.typ == TYP_STAFF

    @property
    def is_merchant(self) -> bool:
        return self.typ == TYP_MERCHANT


async def get_tenant_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> TenantContext:
    """解析 Bearer Token 构建 TenantContext；无效/过期返回 BizError。"""
    if credentials is None or not credentials.credentials:
        raise BizError(ErrorCode.INVALID_TOKEN, "未提供令牌", http_status=401)
    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise BizError(ErrorCode.TOKEN_EXPIRED, http_status=401)
    except jwt.PyJWTError:
        raise BizError(ErrorCode.INVALID_TOKEN, http_status=401)

    sub = payload.get("sub")
    if sub is None:
        raise BizError(ErrorCode.INVALID_TOKEN, http_status=401)

    return TenantContext(
        user_id=int(sub),
        typ=payload.get("typ", TYP_CONSUMER),
        role=payload.get("role", ROLE_CONSUMER),
        merchant_id=payload.get("merchant_id"),
        store_id=payload.get("store_id"),
    )


def require_role(*roles: str) -> Callable[..., Awaitable[TenantContext]]:
    """角色依赖工厂：当前角色不在允许列表内 -> BizError(NO_PERMISSION)。"""

    async def _checker(
        ctx: TenantContext = Depends(get_tenant_context),
    ) -> TenantContext:
        if ctx.role not in roles:
            raise BizError(ErrorCode.NO_PERMISSION)
        return ctx

    return _checker


def tenant_filter(stmt: Select, model: Any, ctx: TenantContext) -> Select:
    """按 TenantContext 自动追加租户过滤条件，避免业务代码手写 if。

    - platform：不过滤（跨商户）。
    - merchant：限 merchant_id。
    - staff：限 merchant_id；核销员/店长进一步限 store_id。
    - consumer：限自身 consumer_id（模型含 consumer_id 时）。
    """
    if ctx.is_platform:
        return stmt

    if ctx.is_consumer:
        if hasattr(model, "consumer_id"):
            return stmt.where(model.consumer_id == ctx.user_id)
        return stmt

    # staff / merchant
    if hasattr(model, "merchant_id"):
        stmt = stmt.where(model.merchant_id == ctx.merchant_id)
    if ctx.is_staff and hasattr(model, "store_id"):
        stmt = stmt.where(model.store_id == ctx.store_id)
    return stmt


def ensure_same_merchant(ctx: TenantContext, merchant_id: int | None) -> None:
    """显式校验资源归属当前商户（用于按 code/唯一键定位后的二次校验）。"""
    if ctx.is_platform:
        return
    if merchant_id is None or merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)


# 兼容显式抛 401 的旧式依赖（保留接口稳定性）
def require_auth() -> Callable[..., Awaitable[TenantContext]]:
    """要求已登录（任意角色）。"""
    return get_tenant_context
