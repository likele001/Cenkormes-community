from alembic import op
import sqlalchemy as sa


revision = "0024_task_equipment_id"
down_revision = "0023_production_calendar_days"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("equipment_id", sa.Integer(), nullable=True))
    op.create_index("ix_tasks_equipment_id", "tasks", ["equipment_id"], unique=False)
    op.create_foreign_key("fk_tasks_equipment_id", "tasks", "equipment", ["equipment_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_tasks_equipment_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_equipment_id", table_name="tasks")
    op.drop_column("tasks", "equipment_id")

