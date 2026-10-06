"""add_ai_employee_tables

Revision ID: 99988930d734
Revises: approval_flows
Create Date: 2026-06-15 07:19:42.010745
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = '99988930d734'
down_revision = 'approval_flows'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('ai_employees',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('role_desc', sa.String(length=200), nullable=True),
    sa.Column('system_prompt', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('bindchannels', mysql.JSON(), nullable=True),
    sa.Column('knowledge_scopes', mysql.JSON(), nullable=True),
    sa.Column('enabled_tools', mysql.JSON(), nullable=True),
    sa.Column('gateway_override', sa.String(length=64), nullable=True),
    sa.Column('welcome_message', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_employees_tenant_id'), 'ai_employees', ['tenant_id'], unique=False)

    op.create_table('ai_employee_conversations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('ai_employee_id', sa.Integer(), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('external_user_id', sa.String(length=100), nullable=True),
    sa.Column('external_user_name', sa.String(length=100), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_employee_conversations_ai_employee_id'), 'ai_employee_conversations', ['ai_employee_id'], unique=False)
    op.create_index(op.f('ix_ai_employee_conversations_tenant_id'), 'ai_employee_conversations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_ai_employee_conversations_user_id'), 'ai_employee_conversations', ['user_id'], unique=False)

    op.create_table('ai_employee_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=16), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('tool_calls', mysql.JSON(), nullable=True),
    sa.Column('tokens_in', sa.Integer(), nullable=True),
    sa.Column('tokens_out', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_employee_messages_conversation_id'), 'ai_employee_messages', ['conversation_id'], unique=False)

    op.create_table('ai_employee_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('ai_employee_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=True),
    sa.Column('detail', mysql.JSON(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_employee_logs_ai_employee_id'), 'ai_employee_logs', ['ai_employee_id'], unique=False)
    op.create_index(op.f('ix_ai_employee_logs_tenant_id'), 'ai_employee_logs', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_employee_logs_tenant_id'), table_name='ai_employee_logs')
    op.drop_index(op.f('ix_ai_employee_logs_ai_employee_id'), table_name='ai_employee_logs')
    op.drop_table('ai_employee_logs')
    op.drop_index(op.f('ix_ai_employee_messages_conversation_id'), table_name='ai_employee_messages')
    op.drop_table('ai_employee_messages')
    op.drop_index(op.f('ix_ai_employee_conversations_user_id'), table_name='ai_employee_conversations')
    op.drop_index(op.f('ix_ai_employee_conversations_tenant_id'), table_name='ai_employee_conversations')
    op.drop_index(op.f('ix_ai_employee_conversations_ai_employee_id'), table_name='ai_employee_conversations')
    op.drop_table('ai_employee_conversations')
    op.drop_index(op.f('ix_ai_employees_tenant_id'), table_name='ai_employees')
    op.drop_table('ai_employees')
