"""wechat_mp_add_push_log_table

微信小程序订阅消息 推送日志表
"""
from alembic import op
import sqlalchemy as sa


revision = 'wechat_mp_add_push_log'
down_revision = ('subcontract_add_logs', '0064_customer_profile')
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT COUNT(*) FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
    ), {"t": table_name})
    return result.scalar() > 0


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "wechat_mp_push_logs"):
        op.create_table(
            "wechat_mp_push_logs",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer, nullable=False, index=True),
            sa.Column("event_code", sa.String(64), nullable=False, index=True),
            sa.Column("target_user_id", sa.Integer, nullable=True, index=True),
            sa.Column("openid", sa.String(64), nullable=False, index=True),
            sa.Column("template_id", sa.String(128), nullable=False),
            sa.Column("page", sa.String(255), nullable=True),
            sa.Column("title", sa.String(128), nullable=False),
            sa.Column("content", sa.Text, nullable=False),
            sa.Column("data_json", sa.Text, nullable=True),
            sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
            sa.Column("error_msg", sa.String(500), nullable=True),
            sa.Column("message_id", sa.String(64), nullable=True),
            sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("sent_at", sa.DateTime, nullable=True),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        # 复合索引（按租户+时间倒序查）
        op.create_index(
            "ix_wechat_mp_push_logs_tenant_created",
            "wechat_mp_push_logs",
            ["tenant_id", sa.text("created_at DESC")],
        )
        op.create_index(
            "ix_wechat_mp_push_logs_tenant_event",
            "wechat_mp_push_logs",
            ["tenant_id", "event_code"],
        )


def downgrade() -> None:
    op.drop_index("ix_wechat_mp_push_logs_tenant_event", table_name="wechat_mp_push_logs")
    op.drop_index("ix_wechat_mp_push_logs_tenant_created", table_name="wechat_mp_push_logs")
    op.drop_table("wechat_mp_push_logs")
