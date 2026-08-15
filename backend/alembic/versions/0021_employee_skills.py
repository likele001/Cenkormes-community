from alembic import op
import sqlalchemy as sa


revision = "0021_employee_skills"
down_revision = "0020_attendance_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_skills_tenant_code"),
    )
    op.create_index("ix_skills_tenant_id", "skills", ["tenant_id"], unique=False)
    op.create_index("ix_skills_code", "skills", ["code"], unique=False)
    op.create_index("ix_skills_is_active", "skills", ["is_active"], unique=False)

    op.create_table(
        "user_skill_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "user_id", "skill_id", name="uq_user_skill_links_tenant_user_skill"),
    )
    op.create_index("ix_user_skill_links_tenant_id", "user_skill_links", ["tenant_id"], unique=False)
    op.create_index("ix_user_skill_links_user_id", "user_skill_links", ["user_id"], unique=False)
    op.create_index("ix_user_skill_links_skill_id", "user_skill_links", ["skill_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_skill_links_skill_id", table_name="user_skill_links")
    op.drop_index("ix_user_skill_links_user_id", table_name="user_skill_links")
    op.drop_index("ix_user_skill_links_tenant_id", table_name="user_skill_links")
    op.drop_table("user_skill_links")

    op.drop_index("ix_skills_is_active", table_name="skills")
    op.drop_index("ix_skills_code", table_name="skills")
    op.drop_index("ix_skills_tenant_id", table_name="skills")
    op.drop_table("skills")
