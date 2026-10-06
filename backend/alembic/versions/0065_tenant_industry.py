"""add industry_code to tenant

Revision ID: 0065_tenant_industry
Revises: add_user_wechat_subs
Create Date: 2026-06-23

"""
from alembic import op
import sqlalchemy as sa

revision = "0065_tenant_industry"
down_revision = "add_user_wechat_subs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("industry_code", sa.String(32), nullable=True))
    op.create_index("ix_tenants_industry_code", "tenants", ["industry_code"])


def downgrade() -> None:
    op.drop_index("ix_tenants_industry_code", table_name="tenants")
    op.drop_column("tenants", "industry_code")
