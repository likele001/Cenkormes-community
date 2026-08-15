from alembic import op
import sqlalchemy as sa


revision = "0022_plan_purchase_links"
down_revision = "0021_employee_skills"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plan_purchase_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["production_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "plan_id", "purchase_order_id", name="uq_plan_purchase_links_tenant_plan_po"),
    )
    op.create_index("ix_plan_purchase_links_tenant_id", "plan_purchase_links", ["tenant_id"], unique=False)
    op.create_index("ix_plan_purchase_links_plan_id", "plan_purchase_links", ["plan_id"], unique=False)
    op.create_index("ix_plan_purchase_links_purchase_order_id", "plan_purchase_links", ["purchase_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_plan_purchase_links_purchase_order_id", table_name="plan_purchase_links")
    op.drop_index("ix_plan_purchase_links_plan_id", table_name="plan_purchase_links")
    op.drop_index("ix_plan_purchase_links_tenant_id", table_name="plan_purchase_links")
    op.drop_table("plan_purchase_links")
