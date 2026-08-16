"""团购套餐 Schema（金额单位：分）。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class PackageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    original_price: int = Field(..., ge=0, description="原价（分）")
    group_price: int = Field(..., ge=0, description="团购价（分）")
    stock: int = Field(default=0, ge=0, description="库存")
    valid_from: str | None = None  # ISO 8601
    valid_to: str | None = None
    images_json: str | None = None
    store_ids: list[int] = Field(default_factory=list, description="适用门店")


class PackageUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    original_price: int | None = Field(default=None, ge=0)
    group_price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    valid_from: str | None = None
    valid_to: str | None = None
    images_json: str | None = None
    store_ids: list[int] | None = None


class PackageOut(BaseModel):
    id: int
    merchant_id: int
    name: str
    description: str | None = None
    original_price: int
    group_price: int
    stock: int
    sold_count: int
    valid_from: str | None = None
    valid_to: str | None = None
    status: str
    images_json: str | None = None
    store_ids: list[int] = []
    created_at: str | None = None
