"""production_plans 下发字段

Revision ID: 0031_plan_release_fields
Revises: 0030_task_assignments
"""

from alembic import op
import sqlalchemy as sa


revision = "0031_plan_release_fields"
down_revision = "0030_task_assignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("production_plans", sa.Column("released_at", sa.DateTime(), nullable=True))
    op.add_column("production_plans", sa.Column("released_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_production_plans_released_by_users",
        "production_plans",
        "users",
        ["released_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_production_plans_released_by", "production_plans", ["released_by"])

    # 兼容历史：已生成工单的订单/计划补全下发信息
    op.execute(
        """
        UPDATE production_plans p
        INNER JOIN work_orders w ON w.order_id = p.order_id AND w.tenant_id = p.tenant_id
        SET p.released_at = COALESCE(p.released_at, p.updated_at),
            p.released_by = COALESCE(p.released_by, p.created_by)
        WHERE p.status IN ('in_progress', 'done') AND p.released_at IS NULL
        """
    )
    op.execute(
        """
        UPDATE orders o
        INNER JOIN work_orders w ON w.order_id = o.id AND w.tenant_id = o.tenant_id
        SET o.status = 'producing'
        WHERE o.status = 'confirmed'
        """
    )


def downgrade() -> None:
    op.drop_index("ix_production_plans_released_by", table_name="production_plans")
    op.drop_constraint("fk_production_plans_released_by_users", "production_plans", type_="foreignkey")
    op.drop_column("production_plans", "released_by")
    op.drop_column("production_plans", "released_at")
