"""计时工资：员工计薪方式、时薪、技能薪资

Revision ID: 0052_hourly_salary
Revises: 0051_shift_management
"""
from alembic import op
import sqlalchemy as sa

revision = "0052_hourly_salary"
down_revision = "0051_shift_management"
branch_labels = None
depends_on = None


def upgrade():
    # users 表加字段
    op.add_column("users", sa.Column("salary_type", sa.String(16), nullable=False, server_default="piece"))
    op.add_column("users", sa.Column("hourly_rate", sa.Numeric(12, 4), nullable=True))

    # salary_items 表：sku_id / process_id 改 nullable，加新字段
    op.alter_column("salary_items", "sku_id", existing_type=sa.Integer(), nullable=True, existing_server_default=None)
    op.alter_column("salary_items", "process_id", existing_type=sa.Integer(), nullable=True, existing_server_default=None)
    op.add_column("salary_items", sa.Column("item_type", sa.String(16), nullable=False, server_default="piece"))
    op.add_column("salary_items", sa.Column("work_hours", sa.Numeric(8, 2), nullable=True))
    op.add_column("salary_items", sa.Column("work_date", sa.Date(), nullable=True))
    op.create_index("ix_salary_items_work_date", "salary_items", ["tenant_id", "user_id", "work_date"])

    # salary_slips 表加字段
    op.add_column("salary_slips", sa.Column("hourly_amount", sa.Numeric(14, 4), nullable=False, server_default="0"))
    op.add_column("salary_slips", sa.Column("hourly_hours", sa.Numeric(10, 2), nullable=False, server_default="0"))


def downgrade():
    op.drop_column("salary_slips", "hourly_hours")
    op.drop_column("salary_slips", "hourly_amount")

    op.drop_index("ix_salary_items_work_date", table_name="salary_items")
    op.drop_column("salary_items", "work_date")
    op.drop_column("salary_items", "work_hours")
    op.drop_column("salary_items", "item_type")
    op.alter_column("salary_items", "process_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("salary_items", "sku_id", existing_type=sa.Integer(), nullable=False)

    op.drop_column("users", "hourly_rate")
    op.drop_column("users", "salary_type")
