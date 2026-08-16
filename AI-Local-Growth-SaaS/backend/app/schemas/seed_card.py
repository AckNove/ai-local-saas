"""种草卡相关 Schema。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SeedCardCreate(BaseModel):
    merchant_id: int = Field(..., description="所属商家 id")
    name: str = Field(..., min_length=1, description="卡片名称")
    type: str = Field(default="二维码", description="NFC/二维码")
    target_type: str = Field(default="video", description="video/private/custom")
    target_url: str = Field(default="", description="跳转目标 URL")
    nfc_id: str | None = Field(default=None, description="NFC 标签 ID（可选）")


class SeedCardOut(BaseModel):
    id: int
    merchant_id: int
    name: str
    slug: str
    type: str = "二维码"
    target_type: str = "video"
    target_url: str = ""
    nfc_id: str | None = None
    qr_code: str | None = None
    status: str = "active"
    created_at: datetime | None = None


class SeedCardSummary(BaseModel):
    id: int
    merchant_id: int
    name: str
    slug: str
    type: str = "二维码"
    target_type: str = "video"
    target_url: str = ""
    status: str = "active"
    created_at: datetime | None = None


class SeedEventIn(BaseModel):
    card_id: int = Field(..., description="种草卡 id")
    event_type: str = Field(..., description="scan/click/share/comment")
    device: str | None = Field(default=None, description="设备类型")
    referer: str | None = Field(default=None, description="来源页")


class SeedEventOut(BaseModel):
    ok: bool = True
    event_id: int
