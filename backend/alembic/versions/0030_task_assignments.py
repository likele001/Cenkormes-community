"""task_assignments 工序多人派工

Revision ID: 0030_task_assignments
Revises: 0029_customer_products
"""

from alembic import op
import sqlalchemy as sa


revision = "0030_task_assignments"
down_revision = "0029_customer_products"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assigned_qty", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "task_id", "user_id", name="uq_task_assignments_task_user"),
    )
    op.create_index("ix_task_assignments_task_id", "task_assignments", ["task_id"])
    op.create_index("ix_task_assignments_tenant_id", "task_assignments", ["tenant_id"])
    op.create_index("ix_task_assignments_user_id", "task_assignments", ["user_id"])
    op.create_index("ix_task_assignments_assigned_by", "task_assignments", ["assigned_by"])

    # 迁移历史单人派工数据
    op.execute(
        """
        INSERT INTO task_assignments (tenant_id, task_id, user_id, assigned_qty, assigned_at, assigned_by)
        SELECT tenant_id, id, assigned_user_id, planned_qty, COALESCE(assigned_at, NOW()), assigned_by
        FROM tasks
        WHERE assigned_user_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_table("task_assignments")
