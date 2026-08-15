"""企业微信消息推送：用户/部门 ID 字段与推送日志

Revision ID: 0047_wecom_notify
Revises: 0046_feishu_cards_oauth
"""
from alembic import op
import sqlalchemy as sa

revision = "0047_wecom_notify"
down_revision = "0046_feishu_cards_oauth"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("wecom_userid", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("wecom_bound_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_wecom_userid", "users", ["wecom_userid"])

    op.add_column("departments", sa.Column("wecom_department_id", sa.String(64), nullable=True))
    op.add_column("departments", sa.Column("wecom_chat_group_code", sa.String(32), nullable=True))

    op.create_table(
        "wecom_push_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_code", sa.String(64), nullable=False),
        sa.Column("target_kind", sa.String(16), nullable=False),
        sa.Column("target_ref", sa.String(128), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("level", sa.String(16), nullable=False, server_default="info"),
        sa.Column("biz_type", sa.String(32), nullable=True),
        sa.Column("biz_id", sa.Integer(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("error_msg", sa.String(500), nullable=True),
        sa.Column("wecom_msgid", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wecom_push_logs_tenant_id", "wecom_push_logs", ["tenant_id"])
    op.create_index("ix_wecom_push_logs_event_code", "wecom_push_logs", ["event_code"])
    op.create_index("ix_wecom_push_logs_status", "wecom_push_logs", ["status"])


def downgrade():
    op.drop_index("ix_wecom_push_logs_status", table_name="wecom_push_logs")
    op.drop_index("ix_wecom_push_logs_event_code", table_name="wecom_push_logs")
    op.drop_index("ix_wecom_push_logs_tenant_id", table_name="wecom_push_logs")
    op.drop_table("wecom_push_logs")

    op.drop_column("departments", "wecom_chat_group_code")
    op.drop_column("departments", "wecom_department_id")

    op.drop_index("ix_users_wecom_userid", table_name="users")
    op.drop_column("users", "wecom_bound_at")
    op.drop_column("users", "wecom_userid")
