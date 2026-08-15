"""Add ai_predict_models table for ML model tracking."""

from alembic import op
import sqlalchemy as sa


revision = "0056_predict_models"
down_revision = "0055_rag_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_predict_models",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False, index=True),
        sa.Column("model_type", sa.String(32), nullable=False, index=True, comment="equipment_health/yield"),
        sa.Column("model_key", sa.String(128), nullable=False, comment="e.g. equipment_id or process_id"),
        sa.Column("trained_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("metrics_json", sa.Text(), nullable=True, comment="training metrics"),
        sa.Column("status", sa.String(16), nullable=False, default="active", server_default="active"),
        sa.Column("data_points", sa.Integer(), nullable=True),
        sa.Column("model_size_bytes", sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_ai_predict_models_tenant_type_key",
        "ai_predict_models",
        ["tenant_id", "model_type", "model_key"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_ai_predict_models_tenant_type_key", "ai_predict_models")
    op.drop_table("ai_predict_models")
