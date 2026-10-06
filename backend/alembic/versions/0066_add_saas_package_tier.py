"""add_saas_package_tier_fields

套餐表增加 tier / max_industries / allowed_industry_codes 字段
"""
from alembic import op
import sqlalchemy as sa


revision = '0066_add_saas_package_tier'
down_revision = '0065_tenant_industry'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # 检查字段是否已存在
    insp = sa.inspect(conn)
    columns = {c["name"] for c in insp.get_columns("saas_packages")}
    
    if "tier" not in columns:
        op.add_column("saas_packages", sa.Column("tier", sa.String(32), nullable=False, server_default="pro"))
        op.alter_column("saas_packages", "tier", server_default=None)
    
    if "max_industries" not in columns:
        op.add_column("saas_packages", sa.Column("max_industries", sa.Integer(), nullable=False, server_default="-1"))
        op.alter_column("saas_packages", "max_industries", server_default=None)
    
    if "allowed_industry_codes" not in columns:
        op.add_column("saas_packages", sa.Column("allowed_industry_codes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("saas_packages", "allowed_industry_codes")
    op.drop_column("saas_packages", "max_industries")
    op.drop_column("saas_packages", "tier")
