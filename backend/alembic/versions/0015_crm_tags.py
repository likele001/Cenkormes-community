from alembic import op
import sqlalchemy as sa


revision = "0015_crm_tags"
down_revision = "0014_crm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_tags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_customer_tags_tenant_name"),
    )
    op.create_index("ix_customer_tags_tenant_id", "customer_tags", ["tenant_id"], unique=False)

    op.create_table(
        "customer_tag_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["customer_tags.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "customer_id", "tag_id", name="uq_customer_tag_links_tenant_customer_tag"),
    )
    op.create_index("ix_customer_tag_links_tenant_id", "customer_tag_links", ["tenant_id"], unique=False)
    op.create_index("ix_customer_tag_links_customer_id", "customer_tag_links", ["customer_id"], unique=False)
    op.create_index("ix_customer_tag_links_tag_id", "customer_tag_links", ["tag_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_customer_tag_links_tag_id", table_name="customer_tag_links")
    op.drop_index("ix_customer_tag_links_customer_id", table_name="customer_tag_links")
    op.drop_index("ix_customer_tag_links_tenant_id", table_name="customer_tag_links")
    op.drop_table("customer_tag_links")

    op.drop_index("ix_customer_tags_tenant_id", table_name="customer_tags")
    op.drop_table("customer_tags")

