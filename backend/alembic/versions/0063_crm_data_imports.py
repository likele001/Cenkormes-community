"""CRM 数据导入任务与错误记录

Revision ID: 0063_crm_data_imports
Revises: 0062_crm_sales_targets
"""
from alembic import op
import sqlalchemy as sa

revision = "0063_crm_data_imports"
down_revision = "0062_crm_sales_targets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_data_import_jobs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("entity_type", sa.String(length=32), nullable=True),
        sa.Column("file_name", sa.String(length=256), nullable=True),
        sa.Column("file_storage_key", sa.String(length=512), nullable=True),
        sa.Column("total_rows", sa.Integer(), nullable=True),
        sa.Column("success_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("field_mapping", sa.JSON(), nullable=True),
        sa.Column("import_mode", sa.String(length=16), nullable=False, server_default="insert_only"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_report_url", sa.String(length=512), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crm_data_import_errors",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("row_index", sa.Integer(), nullable=True),
        sa.Column("field", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=32), nullable=True),
        sa.Column("message", sa.String(length=512), nullable=True),
        sa.Column("raw_value", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_data_import_errors")
    op.drop_table("crm_data_import_jobs")
