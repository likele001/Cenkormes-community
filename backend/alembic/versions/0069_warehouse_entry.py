"""add_warehouse_entry_tables

入库单/入库单明细（Phase4 入库单独立单据化）
"""
from alembic import op
import sqlalchemy as sa


revision = '0069_warehouse_entry'
down_revision = '0068_material_issue'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "warehouse_entries",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("source_type", sa.String(32), nullable=False, server_default="other"),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("purchase_order_id", sa.Integer, sa.ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("material_return_id", sa.Integer, sa.ForeignKey("material_returns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_qty", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
        sa.Column("confirmed_by", sa.Integer, nullable=True),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_warehouse_entries_tenant_code"),
    )
    op.create_index("ix_warehouse_entries_tenant_id", "warehouse_entries", ["tenant_id"])
    op.create_index("ix_warehouse_entries_warehouse_id", "warehouse_entries", ["warehouse_id"])
    op.create_index("ix_warehouse_entries_purchase_order_id", "warehouse_entries", ["purchase_order_id"])
    op.create_index("ix_warehouse_entries_material_return_id", "warehouse_entries", ["material_return_id"])
    op.create_index("ix_warehouse_entries_status", "warehouse_entries", ["status"])

    op.create_table(
        "warehouse_entry_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entry_id", sa.Integer, sa.ForeignKey("warehouse_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_id", sa.Integer, sa.ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sku_id", sa.Integer, sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("cost_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_warehouse_entry_items_tenant_id", "warehouse_entry_items", ["tenant_id"])
    op.create_index("ix_warehouse_entry_items_entry_id", "warehouse_entry_items", ["entry_id"])


def downgrade() -> None:
    op.drop_table("warehouse_entry_items")
    op.drop_table("warehouse_entries")
