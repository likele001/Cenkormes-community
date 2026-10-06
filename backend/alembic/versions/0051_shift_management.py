"""班次管理：班次定义与排班计划

Revision ID: 0051_shift_management
Revises: 0050_dingtalk_notify
"""
from alembic import op
import sqlalchemy as sa

revision = "0051_shift_management"
down_revision = "0050_dingtalk_notify"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "shifts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("rest_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shift_type", sa.String(16), nullable=False, server_default="day"),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_shift_tenant_code"),
    )
    op.create_index("ix_shifts_tenant_id", "shifts", ["tenant_id"])

    op.create_table(
        "shift_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shift_id", sa.Integer(), sa.ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("work_date", sa.String(10), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", "work_date", name="uq_schedule_user_date"),
    )
    op.create_index("ix_shift_schedules_tenant_id", "shift_schedules", ["tenant_id"])
    op.create_index("ix_shift_schedules_user_id", "shift_schedules", ["user_id"])
    op.create_index("ix_shift_schedules_shift_id", "shift_schedules", ["shift_id"])


def downgrade():
    op.drop_index("ix_shift_schedules_shift_id", table_name="shift_schedules")
    op.drop_index("ix_shift_schedules_user_id", table_name="shift_schedules")
    op.drop_index("ix_shift_schedules_tenant_id", table_name="shift_schedules")
    op.drop_table("shift_schedules")

    op.drop_index("ix_shifts_tenant_id", table_name="shifts")
    op.drop_table("shifts")
