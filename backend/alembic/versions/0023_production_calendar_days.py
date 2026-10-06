from alembic import op
import sqlalchemy as sa


revision = "0023_production_calendar_days"
down_revision = "0022_plan_purchase_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "production_calendar_days",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("is_workday", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("capacity_minutes", sa.Integer(), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "day", name="uq_production_calendar_days_tenant_day"),
    )
    op.create_index("ix_production_calendar_days_tenant_id", "production_calendar_days", ["tenant_id"], unique=False)
    op.create_index("ix_production_calendar_days_day", "production_calendar_days", ["day"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_production_calendar_days_day", table_name="production_calendar_days")
    op.drop_index("ix_production_calendar_days_tenant_id", table_name="production_calendar_days")
    op.drop_table("production_calendar_days")

