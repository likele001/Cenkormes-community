from alembic import op
import sqlalchemy as sa


revision = "0011_supplier_statements"
down_revision = "0010_purchase_kitting"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier_statements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("period_from", sa.Date(), nullable=True),
        sa.Column("period_to", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by", sa.Integer(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("paid_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["paid_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_supplier_statements_tenant_code"),
    )
    op.create_index("ix_supplier_statements_tenant_id", "supplier_statements", ["tenant_id"], unique=False)
    op.create_index("ix_supplier_statements_supplier_id", "supplier_statements", ["supplier_id"], unique=False)
    op.create_index("ix_supplier_statements_confirmed_by", "supplier_statements", ["confirmed_by"], unique=False)
    op.create_index("ix_supplier_statements_paid_by", "supplier_statements", ["paid_by"], unique=False)

    op.create_table(
        "supplier_statement_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("statement_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("received_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["statement_id"], ["supplier_statements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "statement_id", "purchase_order_id", name="uq_supplier_statement_items_tenant_stmt_po"),
    )
    op.create_index("ix_supplier_statement_items_tenant_id", "supplier_statement_items", ["tenant_id"], unique=False)
    op.create_index("ix_supplier_statement_items_statement_id", "supplier_statement_items", ["statement_id"], unique=False)
    op.create_index("ix_supplier_statement_items_purchase_order_id", "supplier_statement_items", ["purchase_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_supplier_statement_items_purchase_order_id", table_name="supplier_statement_items")
    op.drop_index("ix_supplier_statement_items_statement_id", table_name="supplier_statement_items")
    op.drop_index("ix_supplier_statement_items_tenant_id", table_name="supplier_statement_items")
    op.drop_table("supplier_statement_items")

    op.drop_index("ix_supplier_statements_paid_by", table_name="supplier_statements")
    op.drop_index("ix_supplier_statements_confirmed_by", table_name="supplier_statements")
    op.drop_index("ix_supplier_statements_supplier_id", table_name="supplier_statements")
    op.drop_index("ix_supplier_statements_tenant_id", table_name="supplier_statements")
    op.drop_table("supplier_statements")
