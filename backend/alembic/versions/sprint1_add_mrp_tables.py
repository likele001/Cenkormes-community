"""sprint1_add_mrp_tables

Revision ID: sprint1_add_mrp
Revises: 0053_cron_jobs
Create Date: 2026-06-14 05:16:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'sprint1_add_mrp'
down_revision = '0053_cron_jobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'mrp_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='running'),
        sa.Column('run_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('scope', sa.String(255), nullable=False, server_default='all'),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_mrp_runs_tenant_code'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_table(
        'mrp_demands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('run_id', sa.Integer(), sa.ForeignKey('mrp_runs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sku_id', sa.Integer(), sa.ForeignKey('skus.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('required_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('in_stock_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('on_order_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shortage_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('suggestion', sa.String(32), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'run_id', 'sku_id', name='uq_mrp_demands_tenant_run_sku'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('mrp_demands')
    op.drop_table('mrp_runs')
