"""工序流转：工单件次 + 追溯码链

Revision ID: 0034_process_flow
Revises: 0033_bom_scope
"""

from alembic import op
import sqlalchemy as sa


revision = "0034_process_flow"
down_revision = "0033_bom_scope"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_order_pieces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=False),
        sa.Column("piece_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="in_progress", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "work_order_id", "piece_no", name="uq_work_order_pieces_tenant_wo_piece"),
    )
    op.create_index("ix_work_order_pieces_tenant_id", "work_order_pieces", ["tenant_id"])
    op.create_index("ix_work_order_pieces_work_order_id", "work_order_pieces", ["work_order_id"])

    op.add_column("report_units", sa.Column("piece_id", sa.Integer(), nullable=True))
    op.add_column("report_units", sa.Column("parent_trace_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_report_units_piece_id",
        "report_units",
        "work_order_pieces",
        ["piece_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_report_units_parent_trace_id",
        "report_units",
        "trace_codes",
        ["parent_trace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_report_units_piece_id", "report_units", ["piece_id"])

    op.add_column("trace_codes", sa.Column("work_order_id", sa.Integer(), nullable=True))
    op.add_column("trace_codes", sa.Column("piece_id", sa.Integer(), nullable=True))
    op.add_column("trace_codes", sa.Column("parent_trace_id", sa.Integer(), nullable=True))
    op.add_column("trace_codes", sa.Column("task_seq", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_trace_codes_work_order_id",
        "trace_codes",
        "work_orders",
        ["work_order_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_trace_codes_piece_id",
        "trace_codes",
        "work_order_pieces",
        ["piece_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_trace_codes_parent_trace_id",
        "trace_codes",
        "trace_codes",
        ["parent_trace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_trace_codes_work_order_id", "trace_codes", ["work_order_id"])
    op.create_index("ix_trace_codes_piece_id", "trace_codes", ["piece_id"])
    op.create_index("ix_trace_codes_parent_trace_id", "trace_codes", ["parent_trace_id"])


def downgrade() -> None:
    op.drop_index("ix_trace_codes_parent_trace_id", table_name="trace_codes")
    op.drop_index("ix_trace_codes_piece_id", table_name="trace_codes")
    op.drop_index("ix_trace_codes_work_order_id", table_name="trace_codes")
    op.drop_constraint("fk_trace_codes_parent_trace_id", "trace_codes", type_="foreignkey")
    op.drop_constraint("fk_trace_codes_piece_id", "trace_codes", type_="foreignkey")
    op.drop_constraint("fk_trace_codes_work_order_id", "trace_codes", type_="foreignkey")
    op.drop_column("trace_codes", "task_seq")
    op.drop_column("trace_codes", "parent_trace_id")
    op.drop_column("trace_codes", "piece_id")
    op.drop_column("trace_codes", "work_order_id")

    op.drop_index("ix_report_units_piece_id", table_name="report_units")
    op.drop_constraint("fk_report_units_parent_trace_id", "report_units", type_="foreignkey")
    op.drop_constraint("fk_report_units_piece_id", "report_units", type_="foreignkey")
    op.drop_column("report_units", "parent_trace_id")
    op.drop_column("report_units", "piece_id")

    op.drop_index("ix_work_order_pieces_work_order_id", table_name="work_order_pieces")
    op.drop_index("ix_work_order_pieces_tenant_id", table_name="work_order_pieces")
    op.drop_table("work_order_pieces")
