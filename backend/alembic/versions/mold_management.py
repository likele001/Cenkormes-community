"""模具/工装管理模块

Revision ID: mold_management
Revises: subcontract_add_logs
"""
from alembic import op
import sqlalchemy as sa


revision = "mold_management"
down_revision = "subcontract_add_logs"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # ---------- 模具台账 ----------
    if "molds" not in existing_tables:
        op.create_table(
            "molds",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("code", sa.String(32), nullable=False),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("model", sa.String(64), nullable=True),
            sa.Column("mold_type", sa.String(32), nullable=False, server_default="injection"),
            sa.Column("workshop", sa.String(64), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="active"),
            sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id", ondelete="SET NULL"), nullable=True),
            sa.Column("expected_lifespan", sa.Integer(), nullable=True),
            sa.Column("current_shots", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("purchase_date", sa.Date(), nullable=True),
            sa.Column("last_maintenance_date", sa.Date(), nullable=True),
            sa.Column("next_maintenance_date", sa.Date(), nullable=True),
            sa.Column("maintenance_interval_shots", sa.Integer(), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("tenant_id", "code", name="uq_molds_tenant_code"),
        )
        op.create_index("ix_molds_tenant_id", "molds", ["tenant_id"])
        op.create_index("ix_molds_sku_id", "molds", ["sku_id"])

    # ---------- 模具维保记录 ----------
    if "mold_maintenance_logs" not in existing_tables:
        op.create_table(
            "mold_maintenance_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("mold_id", sa.Integer(), sa.ForeignKey("molds.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("maintenance_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("shots_at_maintenance", sa.Integer(), nullable=True),
        sa.Column("checked_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # ---------- 模具-工序关联 ----------
    if "mold_process_bindings" not in existing_tables:
        op.create_table(
            "mold_process_bindings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("mold_id", sa.Integer(), sa.ForeignKey("molds.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("process_id", sa.Integer(), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.UniqueConstraint("tenant_id", "mold_id", "process_id", name="uq_mold_process_binding"),
    )


def downgrade():
    op.drop_table("mold_process_bindings")
    op.drop_table("mold_maintenance_logs")
    op.drop_table("molds")
