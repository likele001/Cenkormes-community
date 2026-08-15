"""SPC statistical process control

Revision ID: spc_charts
Revises: mold_management
Create Date: 2025-01-20
"""
from alembic import op
import sqlalchemy as sa

revision = "spc_charts"
down_revision = "mold_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "spc_charts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("chart_type", sa.String(16), nullable=False, server_default="xbar_r"),
        sa.Column("process_id", sa.Integer, sa.ForeignKey("processes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sku_id", sa.Integer, sa.ForeignKey("skus.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sample_size", sa.Integer, nullable=False, server_default="5"),
        sa.Column("ucl", sa.Float, nullable=True),
        sa.Column("lcl", sa.Float, nullable=True),
        sa.Column("target", sa.Float, nullable=True),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_spc_charts_tenant_name"),
    )

    op.create_table(
        "spc_samples",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("chart_id", sa.Integer, sa.ForeignKey("spc_charts.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sample_no", sa.Integer, nullable=False),
        sa.Column("values_json", sa.JSON, nullable=True),
        sa.Column("mean", sa.Float, nullable=True),
        sa.Column("range", sa.Float, nullable=True),
        sa.Column("std_dev", sa.Float, nullable=True),
        sa.Column("defect_count", sa.Integer, nullable=True),
        sa.Column("collected_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("spc_samples")
    op.drop_table("spc_charts")
