"""Configurable approval flow engine

Revision ID: approval_flows
Revises: spc_charts
Create Date: 2025-01-20
"""
from alembic import op
import sqlalchemy as sa

revision = "approval_flows"
down_revision = "spc_charts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_flows",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("biz_type", sa.String(32), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "biz_type", "name", name="uq_approval_flows_tenant_biz_name"),
    )

    op.create_table(
        "approval_steps",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("flow_id", sa.Integer, sa.ForeignKey("approval_flows.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("step_order", sa.Integer, nullable=False),
        sa.Column("approver_role", sa.String(32), nullable=False),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("can_skip", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("label", sa.String(64), nullable=True),
        sa.UniqueConstraint("flow_id", "step_order", name="uq_approval_steps_flow_order"),
    )


def downgrade() -> None:
    op.drop_table("approval_steps")
    op.drop_table("approval_flows")
