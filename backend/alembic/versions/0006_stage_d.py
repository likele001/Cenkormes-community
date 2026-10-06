"""stage_d - 报工/审核/工资

Revision ID: 0006_stage_d
Revises: 0005_stage_c
Create Date: 2026-05-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_stage_d"
down_revision = "0005_stage_c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ----- tasks 加 task_code 并改唯一约束 -----
    op.add_column("tasks", sa.Column("task_code", sa.String(length=32), nullable=False, server_default=""))
    op.create_index("ix_tasks_task_code", "tasks", ["task_code"], unique=False)

    # 旧唯一约束需要先删后建
    op.drop_constraint("uq_tasks_tenant_work_order_seq", "tasks", type_="unique")
    op.create_unique_constraint("uq_tasks_tenant_code", "tasks", ["tenant_id", "task_code"])

    # ----- reports 表 -----
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("report_user_id", sa.Integer(), nullable=False),
        sa.Column("good_qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("bad_qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("attachment_ids", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'submitted'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["report_user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_reports_tenant_id", "reports", ["tenant_id"], unique=False)
    op.create_index("ix_reports_task_id", "reports", ["task_id"], unique=False)
    op.create_index("ix_reports_report_user_id", "reports", ["report_user_id"], unique=False)

    # ----- report_audits 表 -----
    op.create_table(
        "report_audits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("auditor_id", sa.Integer(), nullable=False),
        sa.Column("audit_level", sa.String(length=16), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["auditor_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_report_audits_tenant_id", "report_audits", ["tenant_id"], unique=False)
    op.create_index("ix_report_audits_report_id", "report_audits", ["report_id"], unique=False)

    # ----- salary_items 表 -----
    op.create_table(
        "salary_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("good_qty", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "report_id", name="uq_salary_items_tenant_report"),
    )
    op.create_index("ix_salary_items_tenant_id", "salary_items", ["tenant_id"], unique=False)
    op.create_index("ix_salary_items_report_id", "salary_items", ["report_id"], unique=False)
    op.create_index("ix_salary_items_user_id", "salary_items", ["user_id"], unique=False)
    op.create_index("ix_salary_items_month", "salary_items", ["month"], unique=False)


def downgrade() -> None:
    # salary_items
    op.drop_index("ix_salary_items_month", table_name="salary_items")
    op.drop_index("ix_salary_items_user_id", table_name="salary_items")
    op.drop_index("ix_salary_items_report_id", table_name="salary_items")
    op.drop_index("ix_salary_items_tenant_id", table_name="salary_items")
    op.drop_constraint("uq_salary_items_tenant_report", "salary_items", type_="unique")
    op.drop_table("salary_items")

    # report_audits
    op.drop_index("ix_report_audits_report_id", table_name="report_audits")
    op.drop_index("ix_report_audits_tenant_id", table_name="report_audits")
    op.drop_table("report_audits")

    # reports
    op.drop_index("ix_reports_report_user_id", table_name="reports")
    op.drop_index("ix_reports_task_id", table_name="reports")
    op.drop_index("ix_reports_tenant_id", table_name="reports")
    op.drop_table("reports")

    # tasks
    op.drop_constraint("uq_tasks_tenant_code", "tasks", type_="unique")
    op.create_unique_constraint("uq_tasks_tenant_work_order_seq", "tasks", ["tenant_id", "work_order_id", "seq"])
    op.drop_index("ix_tasks_task_code", table_name="tasks")
    op.drop_column("tasks", "task_code")
