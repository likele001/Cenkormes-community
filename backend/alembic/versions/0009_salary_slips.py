from alembic import op
import sqlalchemy as sa


revision = "0009_salary_slips"
down_revision = "0008_stage_g"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "salary_slips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("item_amount", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("bonus_amount", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("deduction_amount", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("net_amount", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("total_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("signature_attachment_id", sa.Integer(), nullable=True),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["signature_attachment_id"], ["attachments.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "user_id", "month", name="uq_salary_slips_tenant_user_month"),
    )
    op.create_index("ix_salary_slips_tenant_id", "salary_slips", ["tenant_id"], unique=False)
    op.create_index("ix_salary_slips_user_id", "salary_slips", ["user_id"], unique=False)
    op.create_index("ix_salary_slips_month", "salary_slips", ["month"], unique=False)
    op.create_index("ix_salary_slips_signature_attachment_id", "salary_slips", ["signature_attachment_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_salary_slips_signature_attachment_id", table_name="salary_slips")
    op.drop_index("ix_salary_slips_month", table_name="salary_slips")
    op.drop_index("ix_salary_slips_user_id", table_name="salary_slips")
    op.drop_index("ix_salary_slips_tenant_id", table_name="salary_slips")
    op.drop_table("salary_slips")
