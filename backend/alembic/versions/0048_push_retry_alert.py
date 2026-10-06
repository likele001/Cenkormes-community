"""推送日志表添加 retry_count 字段 + 告警接收人设置 + 自动迁移结构

Revision ID: 0048_push_retry_alert
Revises: 0047_wecom_notify
"""
from alembic import op
import sqlalchemy as sa

revision = "0048_push_retry_alert"
down_revision = "0047_wecom_notify"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("feishu_push_logs", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("feishu_push_logs", sa.Column("alerted_at", sa.DateTime(), nullable=True))

    op.add_column("wecom_push_logs", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("wecom_push_logs", sa.Column("alerted_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("wecom_push_logs", "alerted_at")
    op.drop_column("wecom_push_logs", "retry_count")

    op.drop_column("feishu_push_logs", "alerted_at")
    op.drop_column("feishu_push_logs", "retry_count")
