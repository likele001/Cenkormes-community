from alembic import op
import sqlalchemy as sa


revision = "0016_export_jobs"
down_revision = "0015_crm_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "export_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("params_json", sa.Text(), nullable=True),
        sa.Column("result_attachment_id", sa.Integer(), nullable=True),
        sa.Column("celery_task_id", sa.String(length=64), nullable=True),
        sa.Column("error_msg", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["result_attachment_id"], ["attachments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_export_jobs_tenant_id", "export_jobs", ["tenant_id"], unique=False)
    op.create_index("ix_export_jobs_job_type", "export_jobs", ["job_type"], unique=False)
    op.create_index("ix_export_jobs_status", "export_jobs", ["status"], unique=False)
    op.create_index("ix_export_jobs_result_attachment_id", "export_jobs", ["result_attachment_id"], unique=False)
    op.create_index("ix_export_jobs_celery_task_id", "export_jobs", ["celery_task_id"], unique=False)
    op.create_index("ix_export_jobs_created_by", "export_jobs", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_export_jobs_created_by", table_name="export_jobs")
    op.drop_index("ix_export_jobs_celery_task_id", table_name="export_jobs")
    op.drop_index("ix_export_jobs_result_attachment_id", table_name="export_jobs")
    op.drop_index("ix_export_jobs_status", table_name="export_jobs")
    op.drop_index("ix_export_jobs_job_type", table_name="export_jobs")
    op.drop_index("ix_export_jobs_tenant_id", table_name="export_jobs")
    op.drop_table("export_jobs")
