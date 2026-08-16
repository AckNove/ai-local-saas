"""认证相关 Schema。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(..., min_length=1, description="登录名")
    password: str = Field(..., min_length=1, description="密码")


class ChangePasswordIn(BaseModel):
    old_password: str = Field(..., min_length=1, description="原密码")
    new_password: str = Field(..., min_length=6, description="新密码（至少6位）")


class TokenOut(BaseModel):
    token: str = Field(..., description="JWT")
    token_type: str = Field(default="bearer")
    user: "LoginUserOut"


class LoginUserOut(BaseModel):
    id: int
    username: str
    role: str
    merchant_id: int | None = None


class ProfileOut(BaseModel):
    id: int
    username: str
    role: str
    merchant_id: int | None = None
    status: str
    created_at: datetime


# 解决前向引用
TokenOut.model_rebuild()
