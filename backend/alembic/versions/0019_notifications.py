from alembic import op
import sqlalchemy as sa


revision = "0019_notifications"
down_revision = "0018_print_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False, server_default="info"),
        sa.Column("biz_type", sa.String(length=32), nullable=True),
        sa.Column("biz_id", sa.Integer(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_level", "notifications", ["level"], unique=False)
    op.create_index("ix_notifications_biz_type", "notifications", ["biz_type"], unique=False)
    op.create_index("ix_notifications_biz_id", "notifications", ["biz_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notifications_biz_id", table_name="notifications")
    op.drop_index("ix_notifications_biz_type", table_name="notifications")
    op.drop_index("ix_notifications_level", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_tenant_id", table_name="notifications")
    op.drop_table("notifications")
