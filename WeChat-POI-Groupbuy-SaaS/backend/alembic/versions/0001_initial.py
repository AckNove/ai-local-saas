"""initial schema: 14 tables (tenant/catalog/order/fulfillment) + 索引 + 外键 + 软删除

Revision ID: 0001_initial
Revises:
Create Date: 2025-08-13 00:00:00.000000

说明：与 app.models 中 14 张表结构一一对应。支持 SQLite（开发）与 PostgreSQL（生产）。
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ---- platform_operator ----
    op.create_table(
        "platform_operator",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_platform_operator_username", "platform_operator", ["username"], unique=True)

    # ---- merchant ----
    op.create_table(
        "merchant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("logo_url", sa.String(512), nullable=True),
        sa.Column("contact_phone", sa.String(32), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_name", "merchant", ["name"], unique=False)

    # ---- merchant_user ----
    op.create_table(
        "merchant_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_merchant_user_merchant_id", "merchant_user", ["merchant_id"], unique=False)
    op.create_index("ix_merchant_user_username", "merchant_user", ["username"], unique=True)

    # ---- store ----
    op.create_table(
        "store",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("business_hours", sa.String(128), nullable=True),
        sa.Column("poi_id", sa.String(128), nullable=True),
        sa.Column("poi_name", sa.String(255), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_store_merchant_id", "store", ["merchant_id"], unique=False)

    # ---- staff ----
    op.create_table(
        "staff",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("password_hash", sa.String(128), nullable=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("openid", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["store.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_staff_merchant_id", "staff", ["merchant_id"], unique=False)
    op.create_index("ix_staff_store_id", "staff", ["store_id"], unique=False)
    op.create_index("ix_staff_username", "staff", ["username"], unique=True)

    # ---- consumer ----
    op.create_table(
        "consumer",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("openid", sa.String(64), nullable=False),
        sa.Column("unionid", sa.String(64), nullable=True),
        sa.Column("nickname", sa.String(64), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openid"),
    )
    op.create_index("ix_consumer_openid", "consumer", ["openid"], unique=True)

    # ---- group_buy_package ----
    op.create_table(
        "group_buy_package",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("original_price", sa.Integer(), nullable=False),
        sa.Column("group_price", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("sold_count", sa.Integer(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("images_json", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_group_buy_package_merchant_id", "group_buy_package", ["merchant_id"], unique=False)

    # ---- package_store (关联表) ----
    op.create_table(
        "package_store",
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["group_buy_package.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["store.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("package_id", "store_id"),
        sa.UniqueConstraint("package_id", "store_id", name="uq_package_store"),
    )

    # ---- video_channel_binding (先于 orders 以支撑 channel_binding_id FK) ----
    op.create_table(
        "video_channel_binding",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("video_account_id", sa.String(128), nullable=False),
        sa.Column("poi_id", sa.String(128), nullable=True),
        sa.Column("poi_name", sa.String(255), nullable=True),
        sa.Column("groupbuy_link", sa.String(512), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["store.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_video_channel_binding_merchant_id", "video_channel_binding", ["merchant_id"], unique=False)
    op.create_index("ix_video_channel_binding_store_id", "video_channel_binding", ["store_id"], unique=False)

    # ---- orders ----
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_no", sa.String(32), nullable=False),
        sa.Column("consumer_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("commission_amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("fulfillment_type", sa.String(20), nullable=False),
        sa.Column("pickup_status", sa.String(20), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("channel_binding_id", sa.Integer(), nullable=True),
        sa.Column("prepay_id", sa.String(64), nullable=True),
        sa.Column("transaction_id", sa.String(64), nullable=True),
        sa.Column("idempotency_key", sa.String(64), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumer.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["store.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["package_id"], ["group_buy_package.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["channel_binding_id"], ["video_channel_binding.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_order_no", "orders", ["order_no"], unique=True)
    op.create_index("ix_orders_consumer_id", "orders", ["consumer_id"], unique=False)
    op.create_index("ix_orders_merchant_id", "orders", ["merchant_id"], unique=False)
    op.create_index("ix_orders_store_id", "orders", ["store_id"], unique=False)
    op.create_index("ix_orders_idempotency_key", "orders", ["idempotency_key"], unique=True)

    # ---- order_item ----
    op.create_table(
        "order_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_item_order_id", "order_item", ["order_id"], unique=False)

    # ---- verification_code ----
    op.create_table(
        "verification_code",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("order_item_id", sa.Integer(), nullable=True),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("verifier_id", sa.Integer(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_item.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_verification_code_code", "verification_code", ["code"], unique=True)
    op.create_index("ix_verification_code_merchant_id", "verification_code", ["merchant_id"], unique=False)
    op.create_index("ix_verification_code_store_id", "verification_code", ["store_id"], unique=False)
    op.create_index("ix_verification_code_order_id", "verification_code", ["order_id"], unique=False)

    # ---- refund ----
    op.create_table(
        "refund",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("refund_no", sa.String(32), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("consumer_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("channel_refund_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refund_no"),
    )
    op.create_index("ix_refund_refund_no", "refund", ["refund_no"], unique=True)
    op.create_index("ix_refund_order_id", "refund", ["order_id"], unique=False)
    op.create_index("ix_refund_consumer_id", "refund", ["consumer_id"], unique=False)
    op.create_index("ix_refund_merchant_id", "refund", ["merchant_id"], unique=False)

    # ---- reservation ----
    op.create_table(
        "reservation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("consumer_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("reserve_date", sa.Date(), nullable=False),
        sa.Column("time_slot", sa.String(32), nullable=False),
        sa.Column("party_size", sa.Integer(), nullable=False),
        sa.Column("table_no", sa.String(32), nullable=True),
        sa.Column("area", sa.String(64), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("remark", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["store.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumer.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reservation_merchant_id", "reservation", ["merchant_id"], unique=False)
    op.create_index("ix_reservation_store_id", "reservation", ["store_id"], unique=False)
    op.create_index("ix_reservation_consumer_id", "reservation", ["consumer_id"], unique=False)


def downgrade() -> None:
    op.drop_table("reservation")
    op.drop_table("refund")
    op.drop_table("verification_code")
    op.drop_table("order_item")
    op.drop_table("orders")
    op.drop_table("video_channel_binding")
    op.drop_table("package_store")
    op.drop_table("group_buy_package")
    op.drop_table("consumer")
    op.drop_table("staff")
    op.drop_table("store")
    op.drop_table("merchant_user")
    op.drop_table("merchant")
    op.drop_table("platform_operator")
