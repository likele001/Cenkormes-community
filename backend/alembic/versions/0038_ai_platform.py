"""AI platform: models profile, conversations, alerts

Revision ID: 0038_ai_platform
Revises: 0037_order_opportunity_id
"""
from alembic import op
import sqlalchemy as sa

revision = "0038_ai_platform"
down_revision = "0037_order_opportunity_id"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "platform_ai_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("base_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("api_key", sa.Text(), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.execute("INSERT INTO platform_ai_profiles (id, enabled, base_url) VALUES (1, 0, '')")

    op.create_table(
        "platform_ai_models",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("is_vision", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_platform_ai_models_code", "platform_ai_models", ["code"], unique=True)

    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("scene", sa.String(32), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("context_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer(), nullable=False, index=True),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "ai_alert_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False, index=True),
        sa.Column("rule_code", sa.String(64), nullable=False, index=True),
        sa.Column("level", sa.String(16), nullable=False, server_default="warning"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("facts_json", sa.Text(), nullable=True),
        sa.Column("dedupe_key", sa.String(128), nullable=False, index=True),
        sa.Column("notified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade():
    op.drop_table("ai_alert_events")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
    op.drop_index("ix_platform_ai_models_code", table_name="platform_ai_models")
    op.drop_table("platform_ai_models")
    op.drop_table("platform_ai_profiles")
