"""订单 / 核销 / 退款 Schema（金额单位：分）。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """下单入参。"""

    package_id: int = Field(..., gt=0)
    store_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1, le=99)
    phone: str | None = Field(default=None, description="消费者手机")
    fulfillment_type: str = Field(
        default="dine_in", description="dine_in/self_pickup/reservation"
    )
    channel_binding_id: int | None = Field(
        default=None, description="视频号引流归因绑定 ID"
    )


class VerificationCodeOut(BaseModel):
    id: int
    code: str
    status: str
    expires_at: str | None = None


class OrderOut(BaseModel):
    id: int
    order_no: str
    consumer_id: int
    merchant_id: int
    store_id: int
    package_id: int
    quantity: int
    unit_price: int
    total_amount: int
    commission_amount: int
    status: str
    fulfillment_type: str
    pickup_status: str | None = None
    source: str
    channel_binding_id: int | None = None
    paid_at: str | None = None
    expires_at: str | None = None
    phone: str | None = None
    created_at: str | None = None
    verification_codes: list[VerificationCodeOut] = []


class VerifyIn(BaseModel):
    code: str = Field(..., min_length=1, description="核销码")


class PickupUpdateIn(BaseModel):
    """自提备餐状态流转。"""

    status: str = Field(..., description="preparing/ready/picked_up")


class RefundApplyIn(BaseModel):
    order_no: str = Field(..., min_length=1)
    amount: int = Field(..., ge=1, description="退款金额（分）")
    reason: str | None = None


class RefundOut(BaseModel):
    id: int
    refund_no: str
    order_id: int
    amount: int
    reason: str | None = None
    status: str
    channel_refund_id: str | None = None
    created_at: str | None = None
