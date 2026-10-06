"""sprint1_add_subcontract_tables

Revision ID: sprint1_add_subcontract
Revises: sprint1_add_quotation
Create Date: 2026-06-14 05:45:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'sprint1_add_subcontract'
down_revision = 'sprint1_add_quotation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'subcontract_orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_subcontract_orders_tenant_code'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_table(
        'subcontract_order_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('subcontract_orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sku_id', sa.Integer(), sa.ForeignKey('skus.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('sent_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('received_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'order_id', 'sku_id', name='uq_subcontract_items_tenant_order_sku'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('subcontract_order_items')
    op.drop_table('subcontract_orders')
