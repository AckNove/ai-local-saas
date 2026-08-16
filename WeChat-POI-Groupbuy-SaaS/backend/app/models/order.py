"""交易核心模型：Order / OrderItem / VerificationCode / Refund。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, SoftDeleteMixin, utc_now


class Order(Base, SoftDeleteMixin):
    """订单：金额 INT（分）；状态机见架构第 3.1 节。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, comment="订单号 UNIQUE"
    )
    consumer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("consumer.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    package_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("group_buy_package.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, comment="单价（分）")
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="总额（分）")
    commission_amount: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="平台佣金（分，预留）"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending_payment", nullable=False,
        comment="pending_payment/paid/fulfilled/refunded/closed/cancelled",
    )
    fulfillment_type: Mapped[str] = mapped_column(
        String(20), default="dine_in", nullable=False,
        comment="dine_in/self_pickup/reservation",
    )
    pickup_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="preparing/ready/picked_up（仅 self_pickup）"
    )
    source: Mapped[str] = mapped_column(
        String(20), default="in_store", nullable=False,
        comment="in_store/video_channel",
    )
    channel_binding_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("video_channel_binding.id", ondelete="SET NULL"),
        nullable=True, comment="视频号引流归因",
    )
    prepay_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True, comment="支付回调去重（=order_no）"
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="支付超时时间"
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="消费者手机")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class OrderItem(Base):
    """订单明细（快照套餐/门店/单价）。无软删除。"""

    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    package_id: Mapped[int] = mapped_column(Integer, nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, comment="单价（分）")


class VerificationCode(Base):
    """核销码：code 全局 UNIQUE，幂等防重复核销的关键。"""

    __tablename__ = "verification_code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, comment="核销码 UNIQUE"
    )
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    order_item_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("order_item.id", ondelete="RESTRICT"), nullable=True
    )
    merchant_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="unused", nullable=False, comment="unused/used/expired"
    )
    verifier_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class Refund(Base):
    """退款单：refund_no UNIQUE，状态机 pending/processing/succeeded/failed。"""

    __tablename__ = "refund"
    __table_args__ = (UniqueConstraint("refund_no", name="uq_refund_no"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refund_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    consumer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    merchant_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="退款金额（分）")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False,
        comment="pending/processing/succeeded/failed",
    )
    channel_refund_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
