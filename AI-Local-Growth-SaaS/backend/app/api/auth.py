"""认证与用户路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sys_user import SysUser
from app.schemas.auth import ChangePasswordIn, LoginIn, LoginUserOut, ProfileOut, TokenOut
from app.services.auth_service import authenticate
from app.utils.response import bad_request, ok, unauthorized
from app.utils.rbac import get_current_user
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/login")
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    """用户登录，成功返回 JWT 与用户信息。"""
    user = await authenticate(db, body.username, body.password)
    if user is None:
        return unauthorized("用户名或密码错误")

    token = create_access_token(user.id, user.role, user.merchant_id)
    user_out = LoginUserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        merchant_id=user.merchant_id,
    )
    return ok(TokenOut(token=token, token_type="bearer", user=user_out).model_dump())


@router.get("/user/profile")
async def get_profile(current_user: SysUser = Depends(get_current_user)):
    """获取当前登录用户信息（需 Bearer Token）。"""
    out = ProfileOut(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        merchant_id=current_user.merchant_id,
        status=current_user.status,
        created_at=current_user.created_at,
    )
    return ok(out.model_dump())


@router.post("/user/change-password")
async def change_password(
    body: ChangePasswordIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改当前登录用户密码（需验证原密码）。"""
    if not verify_password(body.old_password, current_user.password_hash):
        return bad_request("原密码错误")
    current_user.password_hash = hash_password(body.new_password)
    await db.commit()
    return ok({"changed": True})
