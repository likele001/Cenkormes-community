"""customer_products 客户可下单产品

Revision ID: 0029_customer_products
Revises: 0028_user_profile_fields
"""

from alembic import op
import sqlalchemy as sa


revision = "0029_customer_products"
down_revision = "0028_user_profile_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "customer_id", "product_id", name="uq_customer_products"),
    )
    op.create_index("ix_customer_products_customer_id", "customer_products", ["customer_id"])
    op.create_index("ix_customer_products_product_id", "customer_products", ["product_id"])
    op.create_index("ix_customer_products_tenant_id", "customer_products", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("customer_products")
