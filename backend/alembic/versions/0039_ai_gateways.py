"""多 AI 网关：每网关独立模型列表

Revision ID: 0039_ai_gateways
Revises: 0038_ai_platform
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

revision = "0039_ai_gateways"
down_revision = "0038_ai_platform"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "platform_ai_gateways",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("base_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("api_key", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_platform_ai_gateways_code", "platform_ai_gateways", ["code"], unique=True)

    conn = op.get_bind()
    gw_id = None
    if "platform_ai_profiles" in inspect(conn).get_table_names():
        row = conn.execute(
            text("SELECT enabled, base_url, api_key, timeout_seconds FROM platform_ai_profiles WHERE id = 1")
        ).fetchone()
        if row:
            enabled, base_url, api_key, timeout = row[0], row[1] or "", row[2], row[3] or 120
            conn.execute(
                text(
                    "INSERT INTO platform_ai_gateways "
                    "(code, display_name, base_url, api_key, enabled, is_default, timeout_seconds, sort_order) "
                    "VALUES ('default', '默认网关', :base_url, :api_key, :enabled, 1, :timeout, 0)"
                ),
                {"base_url": base_url, "api_key": api_key, "enabled": 1 if enabled else 0, "timeout": timeout},
            )
            gw_id = conn.execute(text("SELECT id FROM platform_ai_gateways WHERE code = 'default'")).scalar()

    op.add_column("platform_ai_models", sa.Column("gateway_id", sa.Integer(), nullable=True))

    if gw_id:
        conn.execute(text("UPDATE platform_ai_models SET gateway_id = :gid WHERE gateway_id IS NULL"), {"gid": gw_id})

    op.alter_column("platform_ai_models", "gateway_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_platform_ai_models_gateway_id",
        "platform_ai_models",
        "platform_ai_gateways",
        ["gateway_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    try:
        op.drop_index("ix_platform_ai_models_code", table_name="platform_ai_models")
    except Exception:
        pass
    try:
        op.drop_constraint("code", "platform_ai_models", type_="unique")
    except Exception:
        pass
    op.create_index("ix_platform_ai_models_gateway_id", "platform_ai_models", ["gateway_id"], unique=False)
    op.create_unique_constraint("uq_platform_ai_models_gateway_code", "platform_ai_models", ["gateway_id", "code"])


def downgrade():
    op.drop_constraint("uq_platform_ai_models_gateway_code", "platform_ai_models", type_="unique")
    op.drop_constraint("fk_platform_ai_models_gateway_id", "platform_ai_models", type_="foreignkey")
    op.drop_column("platform_ai_models", "gateway_id")
    op.drop_index("ix_platform_ai_gateways_code", table_name="platform_ai_gateways")
    op.drop_table("platform_ai_gateways")
    op.create_index("ix_platform_ai_models_code", "platform_ai_models", ["code"], unique=True)
