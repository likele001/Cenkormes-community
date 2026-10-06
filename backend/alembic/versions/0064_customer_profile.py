"""客户画像与销售聚合字段

Revision ID: 0064_customer_profile
Revises: 0063_crm_data_imports
"""
from alembic import op
import sqlalchemy as sa

revision = "0064_customer_profile"
down_revision = "0063_crm_data_imports"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("customers", sa.Column("lifecycle_stage", sa.String(length=16), nullable=False, server_default="prospect"))
    op.add_column("customers", sa.Column("health_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("health_level", sa.String(length=8), nullable=True))
    op.add_column("customers", sa.Column("risk_flag", sa.String(length=16), nullable=False, server_default="none"))
    op.add_column("customers", sa.Column("industry", sa.String(length=64), nullable=True))
    op.add_column("customers", sa.Column("scale", sa.String(length=32), nullable=True))
    op.add_column("customers", sa.Column("customer_level", sa.String(length=16), nullable=True))
    op.add_column("customers", sa.Column("total_lifetime_value", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("last_order_at", sa.Date(), nullable=True))
    op.add_column("customers", sa.Column("last_order_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("last_follow_up_at", sa.DateTime(), nullable=True))
    op.add_column("customers", sa.Column("open_opportunity_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("open_opportunity_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("active_contract_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("customers", sa.Column("overdue_payment_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"))


def downgrade():
    op.drop_column("customers", "overdue_payment_amount")
    op.drop_column("customers", "active_contract_count")
    op.drop_column("customers", "open_opportunity_amount")
    op.drop_column("customers", "open_opportunity_count")
    op.drop_column("customers", "last_follow_up_at")
    op.drop_column("customers", "last_order_amount")
    op.drop_column("customers", "last_order_at")
    op.drop_column("customers", "total_lifetime_value")
    op.drop_column("customers", "customer_level")
    op.drop_column("customers", "scale")
    op.drop_column("customers", "industry")
    op.drop_column("customers", "risk_flag")
    op.drop_column("customers", "health_level")
    op.drop_column("customers", "health_score")
    op.drop_column("customers", "lifecycle_stage")
