"""飞书卡片 payload 与延迟推送

Revision ID: 0046_feishu_cards_oauth
Revises: 0045_feishu_notify
"""
from alembic import op
import sqlalchemy as sa

revision = "0046_feishu_cards_oauth"
down_revision = "0045_feishu_notify"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("feishu_push_logs", sa.Column("payload_json", sa.Text(), nullable=True))
    op.add_column("feishu_push_logs", sa.Column("scheduled_at", sa.DateTime(), nullable=True))
    op.create_index("ix_feishu_push_logs_scheduled_at", "feishu_push_logs", ["scheduled_at"])


def downgrade():
    op.drop_index("ix_feishu_push_logs_scheduled_at", table_name="feishu_push_logs")
    op.drop_column("feishu_push_logs", "scheduled_at")
    op.drop_column("feishu_push_logs", "payload_json")
