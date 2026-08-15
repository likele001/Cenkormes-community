"""Add ai_rag_feedbacks table for RAG feedback loop."""

from alembic import op
import sqlalchemy as sa


revision = "0055_rag_feedback"
down_revision = "0054_exec_dashboard_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_rag_feedbacks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("feedback_type", sa.String(20), nullable=False, comment="thumb_up/thumb_down/corrected"),
        sa.Column("corrected_answer", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ai_rag_feedbacks")
