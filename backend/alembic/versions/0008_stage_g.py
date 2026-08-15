"""stage_g - 发货/售后/生产计划/设备/字典/补贴扣款

Revision ID: 0008_stage_g
Revises: 0007_stage_f
Create Date: 2026-05-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_stage_g"
down_revision = "0007_stage_f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ----- shipments 表 -----
    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("logistics_company", sa.String(length=128), nullable=True),
        sa.Column("logistics_no", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("shipped_at", sa.DateTime(), nullable=True),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("signed_by", sa.Integer(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["signed_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_shipments_tenant_code"),
    )
    op.create_index("ix_shipments_tenant_id", "shipments", ["tenant_id"], unique=False)
    op.create_index("ix_shipments_order_id", "shipments", ["order_id"], unique=False)

    # ----- after_sales 表 -----
    op.create_table(
        "after_sales",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("trace_code_id", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("sale_type", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["trace_code_id"], ["trace_codes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_after_sales_tenant_code"),
    )
    op.create_index("ix_after_sales_tenant_id", "after_sales", ["tenant_id"], unique=False)
    op.create_index("ix_after_sales_order_id", "after_sales", ["order_id"], unique=False)

    # ----- production_plans 表 -----
    op.create_table(
        "production_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("work_days", sa.Integer(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_production_plans_tenant_code"),
    )
    op.create_index("ix_production_plans_tenant_id", "production_plans", ["tenant_id"], unique=False)
    op.create_index("ix_production_plans_order_id", "production_plans", ["order_id"], unique=False)

    # ----- equipment 表 -----
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=True),
        sa.Column("workshop", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("last_maintenance_date", sa.Date(), nullable=True),
        sa.Column("next_maintenance_date", sa.Date(), nullable=True),
        sa.Column("maintenance_interval_days", sa.Integer(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_equipment_tenant_code"),
    )
    op.create_index("ix_equipment_tenant_id", "equipment", ["tenant_id"], unique=False)

    # ----- equipment_checks 表 -----
    op.create_table(
        "equipment_checks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("check_type", sa.String(length=16), nullable=False),
        sa.Column("result", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("checked_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["checked_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_equipment_checks_tenant_id", "equipment_checks", ["tenant_id"], unique=False)
    op.create_index("ix_equipment_checks_equipment_id", "equipment_checks", ["equipment_id"], unique=False)

    # ----- sys_dict_types 表 -----
    op.create_table(
        "sys_dict_types",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_sys_dict_types_tenant_id", "sys_dict_types", ["tenant_id"], unique=False)

    # ----- sys_dict_items 表 -----
    op.create_table(
        "sys_dict_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("dict_type_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["dict_type_id"], ["sys_dict_types.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_sys_dict_items_dict_type_id", "sys_dict_items", ["dict_type_id"], unique=False)

    # ----- salary_allowances 表 -----
    op.create_table(
        "salary_allowances",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("allowance_type", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Numeric(12, 4), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_salary_allowances_tenant_id", "salary_allowances", ["tenant_id"], unique=False)
    op.create_index("ix_salary_allowances_user_id", "salary_allowances", ["user_id"], unique=False)
    op.create_index("ix_salary_allowances_month", "salary_allowances", ["month"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_salary_allowances_month", table_name="salary_allowances")
    op.drop_index("ix_salary_allowances_user_id", table_name="salary_allowances")
    op.drop_index("ix_salary_allowances_tenant_id", table_name="salary_allowances")
    op.drop_table("salary_allowances")

    op.drop_index("ix_sys_dict_items_dict_type_id", table_name="sys_dict_items")
    op.drop_table("sys_dict_items")

    op.drop_index("ix_sys_dict_types_tenant_id", table_name="sys_dict_types")
    op.drop_table("sys_dict_types")

    op.drop_index("ix_equipment_checks_equipment_id", table_name="equipment_checks")
    op.drop_index("ix_equipment_checks_tenant_id", table_name="equipment_checks")
    op.drop_table("equipment_checks")

    op.drop_index("ix_equipment_tenant_id", table_name="equipment")
    op.drop_constraint("uq_equipment_tenant_code", "equipment", type_="unique")
    op.drop_table("equipment")

    op.drop_index("ix_production_plans_order_id", table_name="production_plans")
    op.drop_index("ix_production_plans_tenant_id", table_name="production_plans")
    op.drop_constraint("uq_production_plans_tenant_code", "production_plans", type_="unique")
    op.drop_table("production_plans")

    op.drop_index("ix_after_sales_order_id", table_name="after_sales")
    op.drop_index("ix_after_sales_tenant_id", table_name="after_sales")
    op.drop_constraint("uq_after_sales_tenant_code", "after_sales", type_="unique")
    op.drop_table("after_sales")

    op.drop_index("ix_shipments_order_id", table_name="shipments")
    op.drop_index("ix_shipments_tenant_id", table_name="shipments")
    op.drop_constraint("uq_shipments_tenant_code", "shipments", type_="unique")
    op.drop_table("shipments")
