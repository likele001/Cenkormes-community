from alembic import op
import sqlalchemy as sa


revision = "0013_finance_ledgers"
down_revision = "0012_purchase_return_stats"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_ledgers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=8), nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("party_type", sa.String(length=16), nullable=False),
        sa.Column("party_id", sa.Integer(), nullable=True),
        sa.Column("statement_type", sa.String(length=32), nullable=True),
        sa.Column("statement_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("biz_date", sa.Date(), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_finance_ledgers_tenant_id", "finance_ledgers", ["tenant_id"], unique=False)
    op.create_index("ix_finance_ledgers_direction", "finance_ledgers", ["direction"], unique=False)
    op.create_index("ix_finance_ledgers_category", "finance_ledgers", ["category"], unique=False)
    op.create_index("ix_finance_ledgers_party_type", "finance_ledgers", ["party_type"], unique=False)
    op.create_index("ix_finance_ledgers_party_id", "finance_ledgers", ["party_id"], unique=False)
    op.create_index("ix_finance_ledgers_statement_type", "finance_ledgers", ["statement_type"], unique=False)
    op.create_index("ix_finance_ledgers_statement_id", "finance_ledgers", ["statement_id"], unique=False)
    op.create_index("ix_finance_ledgers_biz_date", "finance_ledgers", ["biz_date"], unique=False)
    op.create_index("ix_finance_ledgers_created_by", "finance_ledgers", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_finance_ledgers_created_by", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_biz_date", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_statement_id", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_statement_type", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_party_id", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_party_type", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_category", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_direction", table_name="finance_ledgers")
    op.drop_index("ix_finance_ledgers_tenant_id", table_name="finance_ledgers")
    op.drop_table("finance_ledgers")
