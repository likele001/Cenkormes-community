from alembic import op
import sqlalchemy as sa


revision = "0020_attendance_records"
down_revision = "0019_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("check_in_at", sa.DateTime(), nullable=True),
        sa.Column("check_out_at", sa.DateTime(), nullable=True),
        sa.Column("check_in_ip", sa.String(length=64), nullable=True),
        sa.Column("check_out_ip", sa.String(length=64), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "user_id", "work_date", name="uq_attendance_tenant_user_date"),
    )
    op.create_index("ix_attendance_records_tenant_id", "attendance_records", ["tenant_id"], unique=False)
    op.create_index("ix_attendance_records_user_id", "attendance_records", ["user_id"], unique=False)
    op.create_index("ix_attendance_records_work_date", "attendance_records", ["work_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_attendance_records_work_date", table_name="attendance_records")
    op.drop_index("ix_attendance_records_user_id", table_name="attendance_records")
    op.drop_index("ix_attendance_records_tenant_id", table_name="attendance_records")
    op.drop_table("attendance_records")
