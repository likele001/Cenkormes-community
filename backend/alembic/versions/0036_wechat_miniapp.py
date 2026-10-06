"""add wx_miniapp_openid to users

Revision ID: 0036
Revises: 0035
Create Date: 2025-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0036_wechat_miniapp"
down_revision = "0035_product_code"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("wx_miniapp_openid", sa.String(64), nullable=True, index=True),
    )


def downgrade():
    op.drop_column("users", "wx_miniapp_openid")
