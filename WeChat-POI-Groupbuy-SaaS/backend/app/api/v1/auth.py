"""认证路由：wx-login / merchant-login / web-login。"""
from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok
from app.core.security import create_access_token, hash_password, verify_password
from app.core.tenant import (
    ROLE_CONSUMER,
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    ROLE_VERIFIER,
    TYP_CONSUMER,
    TYP_MERCHANT,
    TYP_PLATFORM,
    TYP_STAFF,
    TenantContext,
    get_tenant_context,
)
from app.models.tenant import Consumer, MerchantUser, PlatformOperator, Staff
from app.schemas.auth import ChangePasswordIn, LoginIn, WxLoginIn
from app.schemas.common import TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _resolve_openid(code: str) -> str:
    """wx.login code 换 openid。凭证就绪走真实 jscode2session；否则 Mock 固定映射。"""
    if settings.WECHAT_APPID and settings.WECHAT_SECRET:
        # 真实流程占位：调用 https://api.weixin.qq.com/sns/jscode2session
        raise BizError(ErrorCode.CHANNEL_ERROR, "微信登录真实链路未实现（占位）")
    return "mock_openid_" + hashlib.md5(code.encode("utf-8")).hexdigest()[:16]


async def _find_or_create_consumer(db: AsyncSession, openid: str, nickname: str | None) -> Consumer:
    consumer = await db.scalar(select(Consumer).where(Consumer.openid == openid))
    if consumer is None:
        consumer = Consumer(openid=openid, nickname=nickname or "微信用户")
        db.add(consumer)
        await db.commit()
        await db.refresh(consumer)
    return consumer


@router.post("/wx-login")
async def wx_login(body: WxLoginIn, db: AsyncSession = Depends(get_db)):
    """小程序登录：code -> openid -> 消费者 JWT。"""
    openid = _resolve_openid(body.code)
    consumer = await _find_or_create_consumer(db, openid, body.nickname)
    token = create_access_token(consumer.id, TYP_CONSUMER, ROLE_CONSUMER)
    user = UserOut(
        id=consumer.id, typ=TYP_CONSUMER, role=ROLE_CONSUMER,
        username=None, name=consumer.nickname,
    )
    return ok(TokenOut(token=token, user=user).model_dump())


async def _authenticate_account(db: AsyncSession, username: str, password: str):
    """跨三表校验账号密码，返回 (user_id, typ, role, merchant_id, store_id, name)。"""
    po = await db.scalar(select(PlatformOperator).where(PlatformOperator.username == username))
    if po is not None and po.deleted_at is None and verify_password(password, po.password_hash):
        return po.id, TYP_PLATFORM, ROLE_PLATFORM, None, None, po.username

    mu = await db.scalar(select(MerchantUser).where(MerchantUser.username == username))
    if mu is not None and mu.deleted_at is None and verify_password(password, mu.password_hash):
        return mu.id, TYP_MERCHANT, ROLE_MERCHANT, mu.merchant_id, None, mu.username

    st = await db.scalar(select(Staff).where(Staff.username == username))
    if st is not None and st.deleted_at is None and st.is_active and verify_password(password, st.password_hash or ""):
        return st.id, TYP_STAFF, st.role, st.merchant_id, st.store_id, st.name

    raise BizError(ErrorCode.INVALID_TOKEN, "用户名或密码错误", http_status=401)


@router.post("/merchant-login")
async def merchant_login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    """商户主登录（merchant_owner）。"""
    user_id, typ, role, mid, sid, name = await _authenticate_account(db, body.username, body.password)
    token = create_access_token(user_id, typ, role, mid, sid)
    user = UserOut(id=user_id, typ=typ, role=role, merchant_id=mid, store_id=sid, username=body.username, name=name)
    return ok(TokenOut(token=token, user=user).model_dump())


@router.post("/web-login")
async def web_login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    """Web 后台登录（平台/商户主/店长/核销员）。"""
    user_id, typ, role, mid, sid, name = await _authenticate_account(db, body.username, body.password)
    token = create_access_token(user_id, typ, role, mid, sid)
    user = UserOut(id=user_id, typ=typ, role=role, merchant_id=mid, store_id=sid, username=body.username, name=name)
    return ok(TokenOut(token=token, user=user).model_dump())


@router.post("/change-password")
async def change_password(
    body: ChangePasswordIn,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """修改当前登录账号密码（平台/商户主/店长/核销员，消费者除外）。"""
    if ctx.is_consumer:
        raise BizError(ErrorCode.NO_PERMISSION, "消费者账号不在此修改密码")

    # 按账号类型定位对应表
    if ctx.typ == TYP_PLATFORM:
        account = await db.scalar(select(PlatformOperator).where(PlatformOperator.id == ctx.user_id))
    elif ctx.typ == TYP_MERCHANT:
        account = await db.scalar(select(MerchantUser).where(MerchantUser.id == ctx.user_id))
    elif ctx.typ == TYP_STAFF:
        account = await db.scalar(select(Staff).where(Staff.id == ctx.user_id))
    else:
        raise BizError(ErrorCode.NO_PERMISSION, "该账号类型不支持修改密码")

    if account is None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "账号不存在")

    if not verify_password(body.old_password, account.password_hash or ""):
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "原密码错误")

    account.password_hash = hash_password(body.new_password)
    await db.commit()
    return ok({"changed": True})
