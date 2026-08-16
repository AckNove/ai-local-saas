"""认证请求 Schema。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class WxLoginIn(BaseModel):
    """小程序 wx.login 换 openid 登录。"""

    code: str = Field(..., min_length=1, description="wx.login 返回的临时 code")
    nickname: str | None = Field(default=None, description="首次注册昵称")


class LoginIn(BaseModel):
    """Web/员工登录（平台/商户/店长/核销员）。"""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ChangePasswordIn(BaseModel):
    """修改当前登录账号密码。"""

    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
