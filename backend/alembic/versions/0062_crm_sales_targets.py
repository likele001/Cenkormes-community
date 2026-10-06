"""CRM 销售目标

Revision ID: 0062_crm_sales_targets
Revises: 0061_crm_campaigns
"""
from alembic import op
import sqlalchemy as sa

revision = "0062_crm_sales_targets"
down_revision = "0061_crm_campaigns"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_sales_targets",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("period_type", sa.String(length=16), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("dimension", sa.String(length=16), nullable=True),
        sa.Column("dimension_id", sa.BigInteger(), nullable=True),
        sa.Column("metric", sa.String(length=16), nullable=True),
        sa.Column("target_value", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="CNY"),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_sales_targets")
