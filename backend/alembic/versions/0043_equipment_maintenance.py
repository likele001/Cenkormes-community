"""设备保养计划与保养日志

Revision ID: 0043_equipment_maintenance
Revises: 0042_report_unit_prescreen
"""
from alembic import op
import sqlalchemy as sa

revision = "0043_equipment_maintenance"
down_revision = "3b617c3fe6e7"
branch_labels = None
depends_on = None


def upgrade():
    # ---------- 设备保养计划 ----------
    op.create_table(
        "equipment_maintenance_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("plan_type", sa.String(16), nullable=False),
        sa.Column("check_items", sa.Text(), nullable=True),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("responsible_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("next_date", sa.Date(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ---------- 设备保养日志 ----------
    op.create_table(
        "equipment_maintenance_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("equipment_maintenance_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("check_result", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("attachments", sa.Text(), nullable=True),
        sa.Column("checked_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("equipment_maintenance_logs")
    op.drop_table("equipment_maintenance_plans")
