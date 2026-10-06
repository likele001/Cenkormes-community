"""CRM 营销活动与活动成员

Revision ID: 0061_crm_campaigns
Revises: 0060_crm_win_loss_reasons
"""
from alembic import op
import sqlalchemy as sa

revision = "0061_crm_campaigns"
down_revision = "0060_crm_win_loss_reasons"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_campaigns",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("code", sa.String(length=64), nullable=False, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=True),
        sa.Column("objective", sa.String(length=32), nullable=True),
        sa.Column("target_audience", sa.String(length=256), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="planned"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("budget", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("actual_cost", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("expected_revenue", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("actual_revenue", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="CNY"),
        sa.Column("target_leads_count", sa.Integer(), nullable=True),
        sa.Column("landing_url", sa.String(length=512), nullable=True),
        sa.Column("utm_source", sa.String(length=128), nullable=True),
        sa.Column("utm_campaign", sa.String(length=128), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_campaigns_tenant_code"),
    )

    op.create_table(
        "crm_campaign_members",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("campaign_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("member_type", sa.String(length=16), nullable=True),
        sa.Column("member_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="invited"),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("converted_to_opportunity_id", sa.BigInteger(), nullable=True),
        sa.Column("score_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_campaign_members")
    op.drop_table("crm_campaigns")
