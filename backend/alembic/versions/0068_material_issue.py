"""add_material_issue_return_tables

领料单/领料明细/退料单/退料明细（Phase2 库存成本）
"""
from alembic import op
import sqlalchemy as sa


revision = '0068_material_issue'
down_revision = '0067_add_delivery_mode'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "material_issues",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("work_order_id", sa.Integer, sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_qty", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("issued_at", sa.DateTime, nullable=True),
        sa.Column("issue_by", sa.Integer, nullable=True),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_material_issues_tenant_code"),
    )
    op.create_index("ix_material_issues_tenant_id", "material_issues", ["tenant_id"])
    op.create_index("ix_material_issues_warehouse_id", "material_issues", ["warehouse_id"])
    op.create_index("ix_material_issues_work_order_id", "material_issues", ["work_order_id"])
    op.create_index("ix_material_issues_status", "material_issues", ["status"])

    op.create_table(
        "material_issue_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_id", sa.Integer, sa.ForeignKey("material_issues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_id", sa.Integer, sa.ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sku_id", sa.Integer, sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("cost_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_material_issue_items_tenant_id", "material_issue_items", ["tenant_id"])
    op.create_index("ix_material_issue_items_issue_id", "material_issue_items", ["issue_id"])

    op.create_table(
        "material_returns",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("work_order_id", sa.Integer, sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("issue_id", sa.Integer, sa.ForeignKey("material_issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_qty", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("returned_at", sa.DateTime, nullable=True),
        sa.Column("return_by", sa.Integer, nullable=True),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_material_returns_tenant_code"),
    )
    op.create_index("ix_material_returns_tenant_id", "material_returns", ["tenant_id"])
    op.create_index("ix_material_returns_warehouse_id", "material_returns", ["warehouse_id"])
    op.create_index("ix_material_returns_work_order_id", "material_returns", ["work_order_id"])
    op.create_index("ix_material_returns_status", "material_returns", ["status"])

    op.create_table(
        "material_return_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("return_id", sa.Integer, sa.ForeignKey("material_returns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_item_id", sa.Integer, sa.ForeignKey("material_issue_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("material_id", sa.Integer, sa.ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sku_id", sa.Integer, sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("cost_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_material_return_items_tenant_id", "material_return_items", ["tenant_id"])
    op.create_index("ix_material_return_items_return_id", "material_return_items", ["return_id"])


def downgrade() -> None:
    op.drop_table("material_return_items")
    op.drop_table("material_returns")
    op.drop_table("material_issue_items")
    op.drop_table("material_issues")
