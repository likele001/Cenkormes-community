from alembic import op
import sqlalchemy as sa


revision = "0017_salary_slip_confirm"
down_revision = "0016_export_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("salary_slips", sa.Column("confirm_status", sa.String(length=16), nullable=False, server_default="pending"))
    op.add_column("salary_slips", sa.Column("reject_reason", sa.String(length=255), nullable=True))
    op.add_column("salary_slips", sa.Column("rejected_at", sa.DateTime(), nullable=True))

    op.create_index("ix_salary_slips_confirm_status", "salary_slips", ["confirm_status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_salary_slips_confirm_status", table_name="salary_slips")
    op.drop_column("salary_slips", "rejected_at")
    op.drop_column("salary_slips", "reject_reason")
    op.drop_column("salary_slips", "confirm_status")
