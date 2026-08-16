"""商家与门店相关 Schema。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StoreIn(BaseModel):
    name: str = Field(..., min_length=1, description="门店名称")
    location: str = Field(default="", description="位置")
    video_account: str = Field(default="", description="视频号账号")
    poi_status: str = Field(default="", description="POI 绑定状态")


class StoreOut(BaseModel):
    id: int
    merchant_id: int
    name: str
    location: str = ""
    video_account: str = ""
    poi_status: str = ""
    status: str = "active"


class MerchantCreate(BaseModel):
    name: str = Field(..., min_length=1, description="商家名称")
    industry: str = Field(default="", description="行业")
    address: str = Field(default="", description="地址")
    contact: str = Field(default="", description="联系人")
    phone: str = Field(default="", description="联系电话")
    package: str = Field(default="", description="套餐")
    expire_time: str = Field(default="", description="到期时间")
    stores: list[StoreIn] = Field(default_factory=list, description="初始门店列表")


class MerchantUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    address: str | None = None
    contact: str | None = None
    phone: str | None = None
    package: str | None = None
    expire_time: str | None = None
    status: str | None = None


class DisableIn(BaseModel):
    disabled: bool = Field(..., description="true=禁用, false=启用")


class MerchantOut(BaseModel):
    id: int
    name: str
    industry: str = ""
    address: str = ""
    contact: str = ""
    phone: str = ""
    package: str = ""
    expire_time: str = ""
    status: str = "active"
    created_at: datetime | None = None
    stores: list[StoreOut] = Field(default_factory=list)
