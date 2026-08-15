from alembic import op
import sqlalchemy as sa


revision = "0014_crm"
down_revision = "0013_finance_ledgers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_contacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=64), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "customer_id", "name", "phone", name="uq_customer_contacts_tenant_customer_name_phone"),
    )
    op.create_index("ix_customer_contacts_tenant_id", "customer_contacts", ["tenant_id"], unique=False)
    op.create_index("ix_customer_contacts_customer_id", "customer_contacts", ["customer_id"], unique=False)

    op.create_table(
        "crm_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False, server_default="prospecting"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("amount", sa.Numeric(14, 4), nullable=True),
        sa.Column("probability", sa.Integer(), nullable=True),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_opportunities_tenant_code"),
    )
    op.create_index("ix_crm_opportunities_tenant_id", "crm_opportunities", ["tenant_id"], unique=False)
    op.create_index("ix_crm_opportunities_customer_id", "crm_opportunities", ["customer_id"], unique=False)
    op.create_index("ix_crm_opportunities_owner_user_id", "crm_opportunities", ["owner_user_id"], unique=False)
    op.create_index("ix_crm_opportunities_status", "crm_opportunities", ["status"], unique=False)
    op.create_index("ix_crm_opportunities_stage", "crm_opportunities", ["stage"], unique=False)

    op.create_table(
        "crm_opportunity_activities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("opportunity_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=16), nullable=False, server_default="note"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_crm_opportunity_activities_tenant_id", "crm_opportunity_activities", ["tenant_id"], unique=False)
    op.create_index("ix_crm_opportunity_activities_opportunity_id", "crm_opportunity_activities", ["opportunity_id"], unique=False)
    op.create_index("ix_crm_opportunity_activities_created_by", "crm_opportunity_activities", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_crm_opportunity_activities_created_by", table_name="crm_opportunity_activities")
    op.drop_index("ix_crm_opportunity_activities_opportunity_id", table_name="crm_opportunity_activities")
    op.drop_index("ix_crm_opportunity_activities_tenant_id", table_name="crm_opportunity_activities")
    op.drop_table("crm_opportunity_activities")

    op.drop_index("ix_crm_opportunities_stage", table_name="crm_opportunities")
    op.drop_index("ix_crm_opportunities_status", table_name="crm_opportunities")
    op.drop_index("ix_crm_opportunities_owner_user_id", table_name="crm_opportunities")
    op.drop_index("ix_crm_opportunities_customer_id", table_name="crm_opportunities")
    op.drop_index("ix_crm_opportunities_tenant_id", table_name="crm_opportunities")
    op.drop_table("crm_opportunities")

    op.drop_index("ix_customer_contacts_customer_id", table_name="customer_contacts")
    op.drop_index("ix_customer_contacts_tenant_id", table_name="customer_contacts")
    op.drop_table("customer_contacts")

