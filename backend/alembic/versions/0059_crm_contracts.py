"""CRM 合同与付款计划

Revision ID: 0059_crm_contracts
Revises: 0058_crm_quotations
"""
from alembic import op
import sqlalchemy as sa

revision = "0059_crm_contracts"
down_revision = "0058_crm_quotations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_contracts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("code", sa.String(length=64), nullable=False, index=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("opportunity_id", sa.BigInteger(), nullable=True),
        sa.Column("quotation_id", sa.BigInteger(), nullable=True),
        sa.Column("order_id", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=False, server_default="sales"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("sign_date", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("auto_renewal", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("renewal_notice_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="CNY"),
        sa.Column("payment_terms", sa.String(length=256), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("parent_contract_id", sa.BigInteger(), nullable=True),
        sa.Column("renewal_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("win_loss_reason_id", sa.BigInteger(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_contracts_tenant_code"),
    )

    op.create_table(
        "crm_payment_plans",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("contract_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("phase", sa.String(length=32), nullable=True),
        sa.Column("phase_name", sa.String(length=64), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("actual_amount", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("actual_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("invoice_no", sa.String(length=128), nullable=True),
        sa.Column("remark", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("crm_payment_plans")
    op.drop_table("crm_contracts")
