"""CRM 输赢原因 + 机会字段扩展

Revision ID: 0060_crm_win_loss_reasons
Revises: 0059_crm_contracts
"""
from alembic import op
import sqlalchemy as sa

revision = "0060_crm_win_loss_reasons"
down_revision = "0059_crm_contracts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crm_win_loss_reasons",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("type", sa.String(length=8), nullable=True),
        sa.Column("category", sa.String(length=32), nullable=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_crm_win_loss_reasons_tenant_code"),
    )

    op.add_column("crm_opportunities", sa.Column("win_loss_reason_id", sa.BigInteger(), nullable=True))
    op.add_column("crm_opportunities", sa.Column("win_loss_note", sa.Text(), nullable=True))
    op.add_column("crm_opportunities", sa.Column("campaign_id", sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column("crm_opportunities", "campaign_id")
    op.drop_column("crm_opportunities", "win_loss_note")
    op.drop_column("crm_opportunities", "win_loss_reason_id")
    op.drop_table("crm_win_loss_reasons")
