"""automation_logs

Revision ID: 0041_automation_logs
Revises: 0040_process_skill_links
"""
from alembic import op
import sqlalchemy as sa

revision = "0041_automation_logs"
down_revision = "0040_process_skill_links"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "automation_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trigger", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("biz_type", sa.String(32), nullable=True),
        sa.Column("biz_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("message", sa.String(512), nullable=True),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_automation_logs_tenant_id", "automation_logs", ["tenant_id"])
    op.create_index("ix_automation_logs_trigger", "automation_logs", ["trigger"])
    op.create_index("ix_automation_logs_status", "automation_logs", ["status"])
    op.create_index("ix_automation_logs_biz_id", "automation_logs", ["biz_id"])
    op.create_index("ix_automation_logs_created_at", "automation_logs", ["created_at"])


def downgrade():
    op.drop_index("ix_automation_logs_created_at", table_name="automation_logs")
    op.drop_index("ix_automation_logs_biz_id", table_name="automation_logs")
    op.drop_index("ix_automation_logs_status", table_name="automation_logs")
    op.drop_index("ix_automation_logs_trigger", table_name="automation_logs")
    op.drop_index("ix_automation_logs_tenant_id", table_name="automation_logs")
    op.drop_table("automation_logs")
