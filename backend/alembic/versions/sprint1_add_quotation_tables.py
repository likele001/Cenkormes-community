"""sprint1_add_quotation_tables

Revision ID: sprint1_add_quotation
Revises: sprint1_add_mrp
Create Date: 2026-06-14 05:30:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'sprint1_add_quotation'
down_revision = 'sprint1_add_mrp'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'quotations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('total_amount', sa.Numeric(14, 2), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_quotations_tenant_code'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_table(
        'quotation_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('quotation_id', sa.Integer(), sa.ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('line_no', sa.Integer(), nullable=False),
        sa.Column('sku_id', sa.Integer(), sa.ForeignKey('skus.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('amount', sa.Numeric(14, 2), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'quotation_id', 'line_no', name='uq_quotation_items_tenant_q_line'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('quotation_items')
    op.drop_table('quotations')
