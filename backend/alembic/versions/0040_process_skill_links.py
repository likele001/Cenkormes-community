"""工序-技能绑定

Revision ID: 0040_process_skill_links
Revises: 0039_ai_gateways
"""
from alembic import op
import sqlalchemy as sa

revision = "0040_process_skill_links"
down_revision = "0039_ai_gateways"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "process_skill_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("process_id", sa.Integer(), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("tenant_id", "process_id", "skill_id", name="uq_process_skill_links"),
    )
    op.create_index("ix_process_skill_links_tenant_id", "process_skill_links", ["tenant_id"])
    op.create_index("ix_process_skill_links_process_id", "process_skill_links", ["process_id"])
    op.create_index("ix_process_skill_links_skill_id", "process_skill_links", ["skill_id"])


def downgrade():
    op.drop_index("ix_process_skill_links_skill_id", table_name="process_skill_links")
    op.drop_index("ix_process_skill_links_process_id", table_name="process_skill_links")
    op.drop_index("ix_process_skill_links_tenant_id", table_name="process_skill_links")
    op.drop_table("process_skill_links")
