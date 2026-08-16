"""initial schema: 7 tables (ai_task, merchant_info, store_info, seed_card, seed_event, video_content, sys_user)

Revision ID: 0001_initial
Revises:
Create Date: 2024-08-12 00:00:00.000000

说明：本基线 revision 与 app.models 中 7 张表结构一一对应，用于全新部署。
现有 app.db（由 create_all 创建）不受影响；迁移仅对空库执行。保留 init_db()
中的 create_all 作为兜底。
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
    # ---- ai_task ----
    op.create_table(
        "ai_task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_type", sa.String(32), nullable=False),
        sa.Column("input", sa.JSON(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_task_agent_type", "ai_task", ["agent_type"], unique=False)
    op.create_index("ix_ai_task_status", "ai_task", ["status"], unique=False)

    # ---- merchant_info（含软删除 status）----
    op.create_table(
        "merchant_info",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("industry", sa.String(64), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("contact", sa.String(64), nullable=False),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.Column("package", sa.String(64), nullable=False),
        sa.Column("expire_time", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---- store_info（含软删除 status）----
    op.create_table(
        "store_info",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("video_account", sa.String(128), nullable=False),
        sa.Column("poi_status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_store_info_merchant_id", "store_info", ["merchant_id"], unique=False)

    # ---- seed_card（含软删除 status）----
    op.create_table(
        "seed_card",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("slug", sa.String(32), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("target_type", sa.String(16), nullable=False),
        sa.Column("target_url", sa.String(512), nullable=False),
        sa.Column("nfc_id", sa.String(64), nullable=True),
        sa.Column("qr_code", sa.String(4096), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_seed_card_merchant_id", "seed_card", ["merchant_id"], unique=False)
    op.create_index("ix_seed_card_slug", "seed_card", ["slug"], unique=False)

    # ---- seed_event（只追加审计表）----
    op.create_table(
        "seed_event",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(16), nullable=False),
        sa.Column("device", sa.String(32), nullable=False),
        sa.Column("referer", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_seed_event_card_id", "seed_event", ["card_id"], unique=False)
    op.create_index("ix_seed_event_event_type", "seed_event", ["event_type"], unique=False)
    op.create_index("ix_seed_event_created_at", "seed_event", ["created_at"], unique=False)

    # ---- video_content（含软删除 status）----
    op.create_table(
        "video_content",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("url", sa.String(512), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_video_content_merchant_id", "video_content", ["merchant_id"], unique=False
    )

    # ---- sys_user（含软删除 status）----
    op.create_table(
        "sys_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_sys_user_username", "sys_user", ["username"], unique=False)
    op.create_index("ix_sys_user_merchant_id", "sys_user", ["merchant_id"], unique=False)


def downgrade() -> None:
    op.drop_table("sys_user")
    op.drop_table("video_content")
    op.drop_table("seed_event")
    op.drop_table("seed_card")
    op.drop_table("store_info")
    op.drop_table("merchant_info")
    op.drop_table("ai_task")
