from alembic import op
import sqlalchemy as sa


revision = "0010_purchase_kitting"
down_revision = "0009_salary_slips"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("contact_name", sa.String(length=64), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_suppliers_tenant_code"),
    )
    op.create_index("ix_suppliers_tenant_id", "suppliers", ["tenant_id"], unique=False)

    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("spec", sa.String(length=255), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_materials_tenant_code"),
        sa.UniqueConstraint("tenant_id", "sku_id", name="uq_materials_tenant_sku"),
    )
    op.create_index("ix_materials_tenant_id", "materials", ["tenant_id"], unique=False)
    op.create_index("ix_materials_supplier_id", "materials", ["supplier_id"], unique=False)
    op.create_index("ix_materials_sku_id", "materials", ["sku_id"], unique=False)

    op.create_table(
        "material_boms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "sku_id", name="uq_material_boms_tenant_sku"),
    )
    op.create_index("ix_material_boms_tenant_id", "material_boms", ["tenant_id"], unique=False)
    op.create_index("ix_material_boms_sku_id", "material_boms", ["sku_id"], unique=False)
    op.create_index("ix_material_boms_created_by", "material_boms", ["created_by"], unique=False)

    op.create_table(
        "material_bom_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("bom_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("qty_per", sa.Integer(), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["bom_id"], ["material_boms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "bom_id", "material_id", name="uq_material_bom_items_tenant_bom_material"),
    )
    op.create_index("ix_material_bom_items_tenant_id", "material_bom_items", ["tenant_id"], unique=False)
    op.create_index("ix_material_bom_items_bom_id", "material_bom_items", ["bom_id"], unique=False)
    op.create_index("ix_material_bom_items_material_id", "material_bom_items", ["material_id"], unique=False)

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_purchase_orders_tenant_code"),
    )
    op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"], unique=False)
    op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"], unique=False)
    op.create_index("ix_purchase_orders_confirmed_by", "purchase_orders", ["confirmed_by"], unique=False)
    op.create_index("ix_purchase_orders_created_by", "purchase_orders", ["created_by"], unique=False)

    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("received_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "order_id", "material_id", name="uq_purchase_order_items_tenant_order_material"),
    )
    op.create_index("ix_purchase_order_items_tenant_id", "purchase_order_items", ["tenant_id"], unique=False)
    op.create_index("ix_purchase_order_items_order_id", "purchase_order_items", ["order_id"], unique=False)
    op.create_index("ix_purchase_order_items_material_id", "purchase_order_items", ["material_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_purchase_order_items_material_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_order_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_tenant_id", table_name="purchase_order_items")
    op.drop_table("purchase_order_items")

    op.drop_index("ix_purchase_orders_created_by", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_confirmed_by", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_supplier_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_tenant_id", table_name="purchase_orders")
    op.drop_table("purchase_orders")

    op.drop_index("ix_material_bom_items_material_id", table_name="material_bom_items")
    op.drop_index("ix_material_bom_items_bom_id", table_name="material_bom_items")
    op.drop_index("ix_material_bom_items_tenant_id", table_name="material_bom_items")
    op.drop_table("material_bom_items")

    op.drop_index("ix_material_boms_created_by", table_name="material_boms")
    op.drop_index("ix_material_boms_sku_id", table_name="material_boms")
    op.drop_index("ix_material_boms_tenant_id", table_name="material_boms")
    op.drop_table("material_boms")

    op.drop_index("ix_materials_sku_id", table_name="materials")
    op.drop_index("ix_materials_supplier_id", table_name="materials")
    op.drop_index("ix_materials_tenant_id", table_name="materials")
    op.drop_table("materials")

    op.drop_index("ix_suppliers_tenant_id", table_name="suppliers")
    op.drop_table("suppliers")
