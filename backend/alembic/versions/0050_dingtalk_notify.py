"""钉钉消息推送：用户/部门 ID 字段与推送日志

Revision ID: 0050_dingtalk_notify
Revises: 0049_crm_mes_loop
"""
from alembic import op
import sqlalchemy as sa

revision = "0050_dingtalk_notify"
down_revision = "0049_crm_mes_loop"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("dingtalk_userid", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("dingtalk_union_id", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("dingtalk_bound_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_dingtalk_userid", "users", ["dingtalk_userid"])

    op.add_column("departments", sa.Column("dingtalk_dept_id", sa.String(64), nullable=True))
    op.add_column("departments", sa.Column("dingtalk_chat_group_code", sa.String(32), nullable=True))

    op.create_table(
        "dingtalk_push_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_code", sa.String(64), nullable=False),
        sa.Column("target_kind", sa.String(16), nullable=False),
        sa.Column("target_ref", sa.String(256), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("level", sa.String(16), nullable=False, server_default="info"),
        sa.Column("biz_type", sa.String(32), nullable=True),
        sa.Column("biz_id", sa.Integer(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("error_msg", sa.String(500), nullable=True),
        sa.Column("dingtalk_task_id", sa.String(64), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("alerted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dingtalk_push_logs_tenant_id", "dingtalk_push_logs", ["tenant_id"])
    op.create_index("ix_dingtalk_push_logs_event_code", "dingtalk_push_logs", ["event_code"])
    op.create_index("ix_dingtalk_push_logs_status", "dingtalk_push_logs", ["status"])
    op.create_index("ix_dingtalk_push_logs_scheduled_at", "dingtalk_push_logs", ["scheduled_at"])


def downgrade():
    op.drop_index("ix_dingtalk_push_logs_scheduled_at", table_name="dingtalk_push_logs")
    op.drop_index("ix_dingtalk_push_logs_status", table_name="dingtalk_push_logs")
    op.drop_index("ix_dingtalk_push_logs_event_code", table_name="dingtalk_push_logs")
    op.drop_index("ix_dingtalk_push_logs_tenant_id", table_name="dingtalk_push_logs")
    op.drop_table("dingtalk_push_logs")

    op.drop_column("departments", "dingtalk_chat_group_code")
    op.drop_column("departments", "dingtalk_dept_id")

    op.drop_index("ix_users_dingtalk_userid", table_name="users")
    op.drop_column("users", "dingtalk_bound_at")
    op.drop_column("users", "dingtalk_union_id")
    op.drop_column("users", "dingtalk_userid")
