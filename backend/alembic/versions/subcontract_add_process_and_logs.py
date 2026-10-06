"""subcontract_add_process_and_logs

Revision ID: subcontract_add_logs
Revises: sprint1_add_subcontract
Create Date: 2026-06-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'subcontract_add_logs'
down_revision = 'sprint1_add_subcontract'
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT COUNT(*) FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
    ), {"t": table_name})
    return result.scalar() > 0


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
    ), {"t": table_name, "c": column_name})
    return result.scalar() > 0


def upgrade() -> None:
    conn = op.get_bind()

    # 1. 在 subcontract_order_items 添加 process_id 列（幂等）
    if not _column_exists(conn, 'subcontract_order_items', 'process_id'):
        op.add_column(
            'subcontract_order_items',
            sa.Column('process_id', sa.Integer(),
                      sa.ForeignKey('processes.id', ondelete='SET NULL'),
                      nullable=True, index=True),
        )

    # 2. 创建发料日志表（幂等）
    if not _table_exists(conn, 'subcontract_send_logs'):
        op.create_table(
            'subcontract_send_logs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('order_id', sa.Integer(), sa.ForeignKey('subcontract_orders.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('item_id', sa.Integer(), sa.ForeignKey('subcontract_order_items.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('qty', sa.Integer(), nullable=False),
            sa.Column('remark', sa.Text(), nullable=True),
            sa.Column('sent_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='utf8mb4_general_ci',
            mysql_default_charset='utf8mb4',
            mysql_engine='InnoDB',
        )

    # 3. 创建收货日志表（幂等）
    if not _table_exists(conn, 'subcontract_receive_logs'):
        op.create_table(
            'subcontract_receive_logs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('order_id', sa.Integer(), sa.ForeignKey('subcontract_orders.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('item_id', sa.Integer(), sa.ForeignKey('subcontract_order_items.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('qty', sa.Integer(), nullable=False),
            sa.Column('remark', sa.Text(), nullable=True),
            sa.Column('received_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('received_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='utf8mb4_general_ci',
            mysql_default_charset='utf8mb4',
            mysql_engine='InnoDB',
        )


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, 'subcontract_receive_logs'):
        op.drop_table('subcontract_receive_logs')
    if _table_exists(conn, 'subcontract_send_logs'):
        op.drop_table('subcontract_send_logs')
    if _column_exists(conn, 'subcontract_order_items', 'process_id'):
        op.drop_column('subcontract_order_items', 'process_id')
