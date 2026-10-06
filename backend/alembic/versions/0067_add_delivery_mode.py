"""add_delivery_mode_to_saas_packages

套餐表增加 delivery_mode 字段区分 SaaS 与 源码交付
"""
from alembic import op
import sqlalchemy as sa


revision = '0067_add_delivery_mode'
down_revision = '0066_add_saas_package_tier'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    columns = {c["name"] for c in insp.get_columns("saas_packages")}
    
    if "delivery_mode" not in columns:
        op.add_column("saas_packages", sa.Column("delivery_mode", sa.String(32), nullable=False, server_default="saas"))
        op.alter_column("saas_packages", "delivery_mode", server_default=None)


def downgrade() -> None:
    op.drop_column("saas_packages", "delivery_mode")
