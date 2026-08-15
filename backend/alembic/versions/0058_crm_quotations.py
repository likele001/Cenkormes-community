"""CRM 报价单与报价单行

Revision ID: 0058_crm_quotations
Revises: 0057_crm_leads
"""
from alembic import op
import sqlalchemy as sa

revision = "0058_crm_quotations"
down_revision = "0057_crm_leads"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_quotations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("code", sa.String(length=64), nullable=False, index=True),
        sa.Column("title", sa.String(length=128), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("opportunity_id", sa.BigInteger(), nullable=True),
        sa.Column("contact_id", sa.BigInteger(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="CNY"),
        sa.Column("exchange_rate", sa.Numeric(precision=14, scale=6), nullable=False, server_default="1"),
        sa.Column("tax_rate", sa.Numeric(precision=6, scale=4), nullable=False, server_default="0"),
        sa.Column("discount_rate", sa.Numeric(precision=6, scale=4), nullable=False, server_default="0"),
        sa.Column("subtotal", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("payment_terms", sa.String(length=64), nullable=True),
        sa.Column("delivery_terms", sa.String(length=64), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("reject_reason", sa.String(length=256), nullable=True),
        sa.Column("converted_order_id", sa.BigInteger(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_quotations_tenant_code"),
    )

    op.create_table(
        "crm_quotation_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("quotation_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("sku_id", sa.BigInteger(), nullable=True),
        sa.Column("product_name", sa.String(length=256), nullable=True),
        sa.Column("spec", sa.String(length=256), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("discount_rate", sa.Numeric(precision=6, scale=4), nullable=False, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(precision=6, scale=4), nullable=False, server_default="0"),
        sa.Column("amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("remark", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_quotation_items")
    op.drop_table("crm_quotations")
