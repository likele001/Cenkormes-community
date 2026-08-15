"""add user_wechat_subscriptions table

用户微信小程序订阅消息状态表
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_user_wechat_subs'
down_revision = 'wechat_mp_add_push_log'
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
    if not _table_exists(conn, "user_wechat_subscriptions"):
        op.create_table(
            "user_wechat_subscriptions",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer, nullable=False, index=True),
            sa.Column("user_id", sa.Integer, nullable=False, index=True),
            sa.Column("event_code", sa.String(64), nullable=False),
            sa.Column("template_id", sa.String(128), nullable=False),
            sa.Column("accept_count", sa.Integer, nullable=False, server_default="0"),
            sa.Column("last_accepted_at", sa.DateTime, nullable=True),
            sa.Column("reject_count", sa.Integer, nullable=False, server_default="0"),
            sa.Column("last_rejected_at", sa.DateTime, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("user_id", "event_code", "template_id", name="uq_user_event_template"),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        op.create_index(
            "ix_user_wechat_subs_tenant_user",
            "user_wechat_subscriptions",
            ["tenant_id", "user_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_user_wechat_subs_tenant_user", table_name="user_wechat_subscriptions")
    op.drop_table("user_wechat_subscriptions")
