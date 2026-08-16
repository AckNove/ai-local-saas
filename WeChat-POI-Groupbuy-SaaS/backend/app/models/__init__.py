"""模型包：导入即注册全部 ORM 模型到 Base.metadata。"""
from __future__ import annotations

from app.models.tenant import (
    Consumer,
    Merchant,
    MerchantUser,
    PlatformOperator,
    Staff,
    Store,
)
from app.models.catalog import GroupBuyPackage, PackageStore
from app.models.order import Order, OrderItem, VerificationCode, Refund
from app.models.fulfillment import Reservation, VideoChannelBinding

__all__ = [
    "Consumer",
    "Merchant",
    "MerchantUser",
    "PlatformOperator",
    "Staff",
    "Store",
    "GroupBuyPackage",
    "PackageStore",
    "Order",
    "OrderItem",
    "VerificationCode",
    "Refund",
    "Reservation",
    "VideoChannelBinding",
]
