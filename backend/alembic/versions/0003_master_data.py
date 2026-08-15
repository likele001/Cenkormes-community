"""master_data

Revision ID: 0003_master_data
Revises: 0002_attachments
Create Date: 2026-05-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_master_data"
down_revision = "0002_attachments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_products_tenant_code"),
    )
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"], unique=False)

    op.create_table(
        "skus",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("color", sa.String(length=64), nullable=True),
        sa.Column("material", sa.String(length=128), nullable=True),
        sa.Column("spec", sa.String(length=255), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_skus_tenant_code"),
    )
    op.create_index("ix_skus_tenant_id", "skus", ["tenant_id"], unique=False)
    op.create_index("ix_skus_product_id", "skus", ["product_id"], unique=False)

    op.create_table(
        "processes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("workshop", sa.String(length=64), nullable=True),
        sa.Column("std_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_processes_tenant_code"),
    )
    op.create_index("ix_processes_tenant_id", "processes", ["tenant_id"], unique=False)

    op.create_table(
        "process_routes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "product_id", "name", name="uq_process_routes_tenant_product_name"),
    )
    op.create_index("ix_process_routes_tenant_id", "process_routes", ["tenant_id"], unique=False)
    op.create_index("ix_process_routes_product_id", "process_routes", ["product_id"], unique=False)

    op.create_table(
        "process_route_steps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["route_id"], ["process_routes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "route_id", "seq", name="uq_process_route_steps_tenant_route_seq"),
    )
    op.create_index("ix_process_route_steps_tenant_id", "process_route_steps", ["tenant_id"], unique=False)
    op.create_index("ix_process_route_steps_route_id", "process_route_steps", ["route_id"], unique=False)
    op.create_index("ix_process_route_steps_process_id", "process_route_steps", ["process_id"], unique=False)

    op.create_table(
        "process_prices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "sku_id", "process_id", name="uq_process_prices_tenant_sku_process"),
    )
    op.create_index("ix_process_prices_tenant_id", "process_prices", ["tenant_id"], unique=False)
    op.create_index("ix_process_prices_sku_id", "process_prices", ["sku_id"], unique=False)
    op.create_index("ix_process_prices_process_id", "process_prices", ["process_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_process_prices_process_id", table_name="process_prices")
    op.drop_index("ix_process_prices_sku_id", table_name="process_prices")
    op.drop_index("ix_process_prices_tenant_id", table_name="process_prices")
    op.drop_table("process_prices")

    op.drop_index("ix_process_route_steps_process_id", table_name="process_route_steps")
    op.drop_index("ix_process_route_steps_route_id", table_name="process_route_steps")
    op.drop_index("ix_process_route_steps_tenant_id", table_name="process_route_steps")
    op.drop_table("process_route_steps")

    op.drop_index("ix_process_routes_product_id", table_name="process_routes")
    op.drop_index("ix_process_routes_tenant_id", table_name="process_routes")
    op.drop_table("process_routes")

    op.drop_index("ix_processes_tenant_id", table_name="processes")
    op.drop_table("processes")

    op.drop_index("ix_skus_product_id", table_name="skus")
    op.drop_index("ix_skus_tenant_id", table_name="skus")
    op.drop_table("skus")

    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_table("products")
