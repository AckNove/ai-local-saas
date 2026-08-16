"""租户/门店/员工 CRUD Schema。"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------- Merchant ----------------
class MerchantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    logo_url: str | None = None
    contact_phone: str | None = None
    merchant_code: str | None = Field(default=None, max_length=32, description="小程序商家标识（唯一）")


class MerchantUpdate(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    contact_phone: str | None = None
    merchant_code: str | None = None
    status: str | None = None  # active/disabled


class MerchantOut(BaseModel):
    id: int
    name: str
    logo_url: str | None = None
    contact_phone: str | None = None
    merchant_code: str | None = None
    status: str
    created_at: str | None = None


# ---------------- Store ----------------
class StoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    merchant_id: int | None = Field(
        default=None, description="平台创建门店时必填；商户/店长自动取自身 merchant_id"
    )
    address: str | None = None
    phone: str | None = None
    business_hours: str | None = None
    poi_id: str | None = None
    poi_name: str | None = None
    lng: float | None = None
    lat: float | None = None


class StoreUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    business_hours: str | None = None
    poi_id: str | None = None
    poi_name: str | None = None
    lng: float | None = None
    lat: float | None = None


class StoreOut(BaseModel):
    id: int
    merchant_id: int
    name: str
    address: str | None = None
    phone: str | None = None
    business_hours: str | None = None
    poi_id: str | None = None
    poi_name: str | None = None
    lng: float | None = None
    lat: float | None = None
    created_at: str | None = None


# ---------------- Staff ----------------
class StaffCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    role: str = Field(..., description="store_manager/verifier")
    store_id: int = Field(..., gt=0)
    username: str | None = None
    password: str | None = None
    phone: str | None = None
    openid: str | None = None


class StaffUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    store_id: int | None = None
    phone: str | None = None
    openid: str | None = None
    is_active: bool | None = None


class StaffOut(BaseModel):
    id: int
    merchant_id: int
    store_id: int
    name: str
    role: str
    username: str | None = None
    phone: str | None = None
    openid: str | None = None
    is_active: bool
    created_at: str | None = None
