"""通用 Schema：分页参数、令牌与用户输出。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PageParams(BaseModel):
    """列表查询分页参数（query）。"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UserOut(BaseModel):
    """登录用户输出。"""

    id: int
    typ: str
    role: str
    merchant_id: int | None = None
    store_id: int | None = None
    username: str | None = None
    name: str | None = None


class TokenOut(BaseModel):
    """登录令牌输出。"""

    token: str
    token_type: str = "bearer"
    user: UserOut
