"""stage_f - 溯源/对账/仓储/发货

Revision ID: 0007_stage_f
Revises: 0006_stage_d
Create Date: 2026-05-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_stage_f"
down_revision = "0006_stage_d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ----- trace_codes 表 -----
    op.create_table(
        "trace_codes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_trace_codes_tenant_id", "trace_codes", ["tenant_id"], unique=False)
    op.create_index("ix_trace_codes_code", "trace_codes", ["code"], unique=False)

    # ----- warehouses 表 -----
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_warehouses_tenant_code"),
    )
    op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"], unique=False)

    # ----- stocks 表 -----
    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "warehouse_id", "sku_id", name="uq_stocks_tenant_warehouse_sku"),
    )
    op.create_index("ix_stocks_tenant_id", "stocks", ["tenant_id"], unique=False)
    op.create_index("ix_stocks_warehouse_id", "stocks", ["warehouse_id"], unique=False)
    op.create_index("ix_stocks_sku_id", "stocks", ["sku_id"], unique=False)

    # ----- stock_logs 表 -----
    op.create_table(
        "stock_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("change_qty", sa.Integer(), nullable=False),
        sa.Column("balance_qty", sa.Integer(), nullable=False),
        sa.Column("biz_type", sa.String(length=32), nullable=False),
        sa.Column("biz_id", sa.Integer(), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_stock_logs_tenant_id", "stock_logs", ["tenant_id"], unique=False)
    op.create_index("ix_stock_logs_warehouse_id", "stock_logs", ["warehouse_id"], unique=False)
    op.create_index("ix_stock_logs_sku_id", "stock_logs", ["sku_id"], unique=False)

    # ----- statements 表（对账单） -----
    op.create_table(
        "statements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("total_amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_statements_tenant_code"),
    )
    op.create_index("ix_statements_tenant_id", "statements", ["tenant_id"], unique=False)
    op.create_index("ix_statements_customer_id", "statements", ["customer_id"], unique=False)

    # ----- statement_items 表（对账单明细） -----
    op.create_table(
        "statement_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("statement_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["statement_id"], ["statements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "statement_id", "order_id", name="uq_statement_items_tenant_stmt_order"),
    )
    op.create_index("ix_statement_items_tenant_id", "statement_items", ["tenant_id"], unique=False)
    op.create_index("ix_statement_items_statement_id", "statement_items", ["statement_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_statement_items_statement_id", table_name="statement_items")
    op.drop_index("ix_statement_items_tenant_id", table_name="statement_items")
    op.drop_constraint("uq_statement_items_tenant_stmt_order", "statement_items", type_="unique")
    op.drop_table("statement_items")

    op.drop_index("ix_statements_customer_id", table_name="statements")
    op.drop_index("ix_statements_tenant_id", table_name="statements")
    op.drop_constraint("uq_statements_tenant_code", "statements", type_="unique")
    op.drop_table("statements")

    op.drop_index("ix_stock_logs_sku_id", table_name="stock_logs")
    op.drop_index("ix_stock_logs_warehouse_id", table_name="stock_logs")
    op.drop_index("ix_stock_logs_tenant_id", table_name="stock_logs")
    op.drop_table("stock_logs")

    op.drop_index("ix_stocks_sku_id", table_name="stocks")
    op.drop_index("ix_stocks_warehouse_id", table_name="stocks")
    op.drop_index("ix_stocks_tenant_id", table_name="stocks")
    op.drop_constraint("uq_stocks_tenant_warehouse_sku", "stocks", type_="unique")
    op.drop_table("stocks")

    op.drop_index("ix_warehouses_tenant_id", table_name="warehouses")
    op.drop_constraint("uq_warehouses_tenant_code", "warehouses", type_="unique")
    op.drop_table("warehouses")

    op.drop_index("ix_trace_codes_code", table_name="trace_codes")
    op.drop_index("ix_trace_codes_tenant_id", table_name="trace_codes")
    op.drop_table("trace_codes")
