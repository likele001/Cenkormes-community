"""报工件次 report_units

Revision ID: 0032_report_units
Revises: 0031_plan_release_fields
"""

from alembic import op
import sqlalchemy as sa


revision = "0032_report_units"
down_revision = "0031_plan_release_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_units",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("task_assignment_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("unit_seq", sa.Integer(), nullable=False),
        sa.Column("result_type", sa.String(length=16), nullable=True),
        sa.Column("employee_attachment_ids", sa.String(length=512), nullable=True),
        sa.Column("qc_attachment_ids", sa.String(length=512), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="draft", nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["task_assignment_id"], ["task_assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "task_assignment_id", "unit_seq", name="uq_report_units_tenant_assignment_seq"),
    )
    op.create_index("ix_report_units_tenant_id", "report_units", ["tenant_id"])
    op.create_index("ix_report_units_task_assignment_id", "report_units", ["task_assignment_id"])
    op.create_index("ix_report_units_task_id", "report_units", ["task_id"])
    op.create_index("ix_report_units_user_id", "report_units", ["user_id"])
    op.create_index("ix_report_units_status", "report_units", ["status"])

    op.create_table(
        "report_unit_audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("report_unit_id", sa.Integer(), nullable=False),
        sa.Column("auditor_id", sa.Integer(), nullable=False),
        sa.Column("audit_level", sa.String(length=16), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("attachment_ids", sa.String(length=512), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["auditor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["report_unit_id"], ["report_units.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_report_unit_audits_tenant_id", "report_unit_audits", ["tenant_id"])
    op.create_index("ix_report_unit_audits_report_unit_id", "report_unit_audits", ["report_unit_id"])

    op.add_column("salary_items", sa.Column("report_unit_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_salary_items_report_unit_id",
        "salary_items",
        "report_units",
        ["report_unit_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_salary_items_report_unit_id", "salary_items", ["report_unit_id"])
    op.create_unique_constraint("uq_salary_items_tenant_report_unit", "salary_items", ["tenant_id", "report_unit_id"])

    op.alter_column("salary_items", "report_id", existing_type=sa.Integer(), nullable=True)

    op.add_column("trace_codes", sa.Column("report_unit_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_trace_codes_report_unit_id",
        "trace_codes",
        "report_units",
        ["report_unit_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_trace_codes_report_unit_id", "trace_codes", ["report_unit_id"])
    op.alter_column("trace_codes", "report_id", existing_type=sa.Integer(), nullable=True)

    # 为已有派工预生成件次槽位
    op.execute(
        """
        INSERT INTO report_units (tenant_id, task_assignment_id, task_id, user_id, unit_seq, status, created_at, updated_at)
        SELECT ta.tenant_id, ta.id, ta.task_id, ta.user_id, n.seq, 'draft', NOW(), NOW()
        FROM task_assignments ta
        JOIN (
            SELECT 1 AS seq UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
            UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
            UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
            UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
            UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
            UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
            UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
            UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
            UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
            UNION SELECT 46 UNION SELECT 47 UNION SELECT 48 UNION SELECT 49 UNION SELECT 50
        ) n ON n.seq <= ta.assigned_qty
        WHERE NOT EXISTS (
            SELECT 1 FROM report_units ru
            WHERE ru.task_assignment_id = ta.id AND ru.unit_seq = n.seq
        )
        """
    )


def downgrade() -> None:
    op.alter_column("trace_codes", "report_id", existing_type=sa.Integer(), nullable=False)
    op.drop_index("ix_trace_codes_report_unit_id", table_name="trace_codes")
    op.drop_constraint("fk_trace_codes_report_unit_id", "trace_codes", type_="foreignkey")
    op.drop_column("trace_codes", "report_unit_id")

    op.alter_column("salary_items", "report_id", existing_type=sa.Integer(), nullable=False)
    op.drop_constraint("uq_salary_items_tenant_report_unit", "salary_items", type_="unique")
    op.drop_index("ix_salary_items_report_unit_id", table_name="salary_items")
    op.drop_constraint("fk_salary_items_report_unit_id", "salary_items", type_="foreignkey")
    op.drop_column("salary_items", "report_unit_id")

    op.drop_index("ix_report_unit_audits_report_unit_id", table_name="report_unit_audits")
    op.drop_index("ix_report_unit_audits_tenant_id", table_name="report_unit_audits")
    op.drop_table("report_unit_audits")
    op.drop_index("ix_report_units_status", table_name="report_units")
    op.drop_index("ix_report_units_user_id", table_name="report_units")
    op.drop_index("ix_report_units_task_id", table_name="report_units")
    op.drop_index("ix_report_units_task_assignment_id", table_name="report_units")
    op.drop_index("ix_report_units_tenant_id", table_name="report_units")
    op.drop_table("report_units")
