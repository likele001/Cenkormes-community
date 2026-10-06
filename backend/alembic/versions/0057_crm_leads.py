"""CRM 线索与线索活动

Revision ID: 0057_crm_leads
Revises: 0056_predict_models
"""
from alembic import op
import sqlalchemy as sa

revision = "0057_crm_leads"
down_revision = "0056_predict_models"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_leads",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("code", sa.String(length=64), nullable=False, index=True),
        sa.Column("contact_name", sa.String(length=64), nullable=False),
        sa.Column("company", sa.String(length=128), nullable=True, index=True),
        sa.Column("email", sa.String(length=128), nullable=True, index=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("mobile", sa.String(length=32), nullable=True),
        sa.Column("wechat", sa.String(length=64), nullable=True),
        sa.Column("position", sa.String(length=64), nullable=True),
        sa.Column("industry", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=True),
        sa.Column("province", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("address", sa.String(length=256), nullable=True),
        sa.Column("website", sa.String(length=256), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column("interest_products", sa.JSON(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="new"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grade", sa.String(length=8), nullable=True),
        sa.Column("last_follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("next_follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("is_public_pool", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("campaign_id", sa.BigInteger(), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=True, index=True),
        sa.Column("opportunity_id", sa.BigInteger(), nullable=True, index=True),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
        sa.Column("converted_by", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_leads_tenant_code"),
    )

    op.create_table(
        "crm_lead_activities",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("lead_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("action_type", sa.String(length=16), nullable=False, server_default="note"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("next_follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_lead_activities")
    op.drop_table("crm_leads")
