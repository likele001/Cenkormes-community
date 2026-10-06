"""BOM 作用域：型号专属 / 产品默认 / 全厂默认

Revision ID: 0033_bom_scope
Revises: 0032_report_units
"""

from alembic import op
import sqlalchemy as sa


revision = "0033_bom_scope"
down_revision = "0032_report_units"
branch_labels = None
depends_on = None

BOM_SCOPE_SKU = "sku"
BOM_SCOPE_PRODUCT = "product"
BOM_SCOPE_GLOBAL = "global"


def upgrade() -> None:
    op.add_column("material_boms", sa.Column("scope", sa.String(length=16), nullable=False, server_default=BOM_SCOPE_SKU))
    op.add_column("material_boms", sa.Column("product_id", sa.Integer(), nullable=True))
    op.add_column("material_boms", sa.Column("name", sa.String(length=128), nullable=True))
    op.add_column("material_boms", sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    op.create_foreign_key(
        "fk_material_boms_product_id",
        "material_boms",
        "products",
        ["product_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_material_boms_product_id", "material_boms", ["product_id"], unique=False)
    op.create_index("ix_material_boms_scope", "material_boms", ["tenant_id", "scope"], unique=False)

    op.drop_constraint("uq_material_boms_tenant_sku", "material_boms", type_="unique")
    op.alter_column("material_boms", "sku_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute(
        "UPDATE material_boms SET sku_id = 0 WHERE sku_id IS NULL AND scope != 'sku'"
    )
    op.alter_column("material_boms", "sku_id", existing_type=sa.Integer(), nullable=False)
    op.create_unique_constraint("uq_material_boms_tenant_sku", "material_boms", ["tenant_id", "sku_id"])

    op.drop_index("ix_material_boms_scope", table_name="material_boms")
    op.drop_index("ix_material_boms_product_id", table_name="material_boms")
    op.drop_constraint("fk_material_boms_product_id", "material_boms", type_="foreignkey")
    op.drop_column("material_boms", "is_default")
    op.drop_column("material_boms", "name")
    op.drop_column("material_boms", "product_id")
    op.drop_column("material_boms", "scope")
