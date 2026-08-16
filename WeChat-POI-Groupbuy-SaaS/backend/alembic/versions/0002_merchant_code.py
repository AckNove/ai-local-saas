"""add merchant_code to merchant

Revision ID: 0002_merchant_code
Revises: 0001_initial
Create Date: 2026-08-16

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_merchant_code"
down_revision: str | None = "0001_initial"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("merchant", sa.Column("merchant_code", sa.String(32), nullable=True))
    op.create_index("ix_merchant_merchant_code", "merchant", ["merchant_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_merchant_merchant_code", table_name="merchant")
    op.drop_column("merchant", "merchant_code")
