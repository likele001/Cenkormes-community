from alembic import op
import sqlalchemy as sa


revision = "0018_print_templates"
down_revision = "0017_salary_slip_confirm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "print_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("template_type", sa.String(length=32), nullable=False, server_default="html"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_print_templates_tenant_code"),
    )
    op.create_index("ix_print_templates_tenant_id", "print_templates", ["tenant_id"], unique=False)
    op.create_index("ix_print_templates_code", "print_templates", ["code"], unique=False)
    op.create_index("ix_print_templates_template_type", "print_templates", ["template_type"], unique=False)
    op.create_index("ix_print_templates_is_active", "print_templates", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_print_templates_is_active", table_name="print_templates")
    op.drop_index("ix_print_templates_template_type", table_name="print_templates")
    op.drop_index("ix_print_templates_code", table_name="print_templates")
    op.drop_index("ix_print_templates_tenant_id", table_name="print_templates")
    op.drop_table("print_templates")
