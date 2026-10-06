"""code_sequences table

Revision ID: 0027_code_sequences
Revises: 0026_saas_platform
"""

from alembic import op
import sqlalchemy as sa


revision = "0027_code_sequences"
down_revision = "0026_saas_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_sequences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("biz_type", sa.String(length=32), nullable=False),
        sa.Column("period_key", sa.String(length=16), nullable=False, server_default=""),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "biz_type", "period_key", name="uq_code_sequences"),
    )
    op.create_index("ix_code_sequences_tenant_id", "code_sequences", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_code_sequences_tenant_id", table_name="code_sequences")
    op.drop_table("code_sequences")
