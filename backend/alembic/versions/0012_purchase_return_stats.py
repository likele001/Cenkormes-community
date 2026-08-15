"""purchase return and stats

Revision ID: 0012_purchase_return_stats
Revises: 0011_supplier_statements
Create Date: 2026-05-21 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_purchase_return_stats"
down_revision = "0011_supplier_statements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("purchase_order_items", sa.Column("returned_qty", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("purchase_order_items", "returned_qty")
