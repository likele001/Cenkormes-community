"""SaaS platform: tenant extensions, invites, platform users, packages, subscriptions

Revision ID: 0026_saas_platform
Revises: 0025_performance_indexes
"""

from alembic import op
import sqlalchemy as sa


revision = "0026_saas_platform"
down_revision = "0025_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tenants", sa.Column("status", sa.String(32), nullable=False, server_default="active"))
    op.add_column("tenants", sa.Column("subscription_expires_at", sa.DateTime(), nullable=True))
    op.add_column("tenants", sa.Column("current_package_id", sa.Integer(), nullable=True))
    op.add_column("tenants", sa.Column("custom_domain", sa.String(64), nullable=True))
    op.add_column("tenants", sa.Column("logo_url", sa.String(512), nullable=True))
    op.add_column("tenants", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_platform_settings_key"),
    )

    op.create_table(
        "platform_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_platform_users_username"),
    )

    op.create_table(
        "saas_packages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("price_yuan", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("duration_days", sa.Integer(), nullable=False, server_default="365"),
        sa.Column("max_users", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("features_json", sa.Text(), nullable=True),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_saas_packages_code"),
    )

    op.create_foreign_key(
        "fk_tenants_current_package_id",
        "tenants",
        "saas_packages",
        ["current_package_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "tenant_subscriptions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["package_id"], ["saas_packages.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenant_subscriptions_tenant_id", "tenant_subscriptions", ["tenant_id"])

    op.create_table(
        "subscription_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_no", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("amount_yuan", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("remark", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["package_id"], ["saas_packages.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_no", name="uq_subscription_orders_order_no"),
    )

    op.create_table(
        "tenant_invites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("role_code", sa.String(32), nullable=False, server_default="employee"),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_tenant_invites_token"),
    )
    op.create_index("ix_tenant_invites_tenant_id", "tenant_invites", ["tenant_id"])

    # seed default platform settings
    op.execute(
        "INSERT INTO platform_settings (`key`, `value`) VALUES "
        "('saas_mode_enabled', 'false'), "
        "('xunhu_app_id', ''), "
        "('xunhu_app_secret', ''), "
        "('xunhu_gateway', 'https://api.xunhupay.com/payment/do.html'), "
        "('default_trial_days', '14')"
    )


def downgrade():
    op.drop_table("tenant_invites")
    op.drop_table("subscription_orders")
    op.drop_table("tenant_subscriptions")
    op.drop_constraint("fk_tenants_current_package_id", "tenants", type_="foreignkey")
    op.drop_table("saas_packages")
    op.drop_table("platform_users")
    op.drop_table("platform_settings")
    op.drop_column("tenants", "updated_at")
    op.drop_column("tenants", "logo_url")
    op.drop_column("tenants", "custom_domain")
    op.drop_column("tenants", "current_package_id")
    op.drop_column("tenants", "subscription_expires_at")
    op.drop_column("tenants", "status")
