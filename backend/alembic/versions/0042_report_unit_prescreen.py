"""report_units 预审字段

Revision ID: 0042_report_unit_prescreen
Revises: 0041_automation_logs
"""
from alembic import op
import sqlalchemy as sa

revision = "0042_report_unit_prescreen"
down_revision = "0041_automation_logs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("report_units", sa.Column("prescreen_level", sa.String(16), nullable=True))
    op.add_column("report_units", sa.Column("prescreen_json", sa.Text(), nullable=True))
    op.add_column("report_units", sa.Column("prescreen_at", sa.DateTime(), nullable=True))
    op.create_index("ix_report_units_prescreen_level", "report_units", ["prescreen_level"])


def downgrade():
    op.drop_index("ix_report_units_prescreen_level", table_name="report_units")
    op.drop_column("report_units", "prescreen_at")
    op.drop_column("report_units", "prescreen_json")
    op.drop_column("report_units", "prescreen_level")
