"""考勤 GPS 定位字段

Revision ID: 0044_attendance_gps
Revises: 0043_equipment_maintenance
"""
from alembic import op
import sqlalchemy as sa

revision = "0044_attendance_gps"
down_revision = "0043_equipment_maintenance"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("attendance_records", sa.Column("check_in_lat", sa.Float(), nullable=True))
    op.add_column("attendance_records", sa.Column("check_in_lng", sa.Float(), nullable=True))
    op.add_column("attendance_records", sa.Column("check_out_lat", sa.Float(), nullable=True))
    op.add_column("attendance_records", sa.Column("check_out_lng", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("attendance_records", "check_out_lng")
    op.drop_column("attendance_records", "check_out_lat")
    op.drop_column("attendance_records", "check_in_lng")
    op.drop_column("attendance_records", "check_in_lat")
