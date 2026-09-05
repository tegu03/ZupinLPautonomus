"""Require chain identity for daily PnL rows.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "daily_pnl",
        "chain_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "daily_pnl",
        "chain_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
