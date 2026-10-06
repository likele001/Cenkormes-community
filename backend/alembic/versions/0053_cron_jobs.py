"""定时任务调度配置表

Revision ID: 0053_cron_jobs
Revises: 0052_hourly_salary
"""
from alembic import op
import sqlalchemy as sa

revision = "0053_cron_jobs"
down_revision = "0052_hourly_salary"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cron_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False, comment="调度唯一标识"),
        sa.Column("task_name", sa.String(256), nullable=False, comment="Celery 任务路径"),
        sa.Column("description", sa.String(256), nullable=True, comment="中文描述"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true(), comment="是否启用"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false(), comment="是否系统默认任务"),
        sa.Column("cron_minute", sa.String(64), nullable=False, server_default="0", comment="分钟"),
        sa.Column("cron_hour", sa.String(64), nullable=False, server_default="*", comment="小时"),
        sa.Column("cron_day_of_month", sa.String(64), nullable=False, server_default="*", comment="日"),
        sa.Column("cron_month_of_year", sa.String(64), nullable=False, server_default="*", comment="月"),
        sa.Column("cron_day_of_week", sa.String(64), nullable=False, server_default="*", comment="星期"),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_cron_jobs_name", "cron_jobs", ["name"])
    op.create_index("ix_cron_jobs_enabled", "cron_jobs", ["enabled"])


def downgrade():
    op.drop_index("ix_cron_jobs_enabled", table_name="cron_jobs")
    op.drop_index("ix_cron_jobs_name", table_name="cron_jobs")
    op.drop_table("cron_jobs")
