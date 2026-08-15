"""users / platform_users 增加手机、邮箱

Revision ID: 0028_user_profile_fields
Revises: 0027_code_sequences
"""

from alembic import op
import sqlalchemy as sa


revision = "0028_user_profile_fields"
down_revision = "0027_code_sequences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(length=128), nullable=True))
    op.add_column("platform_users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("platform_users", sa.Column("email", sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column("platform_users", "email")
    op.drop_column("platform_users", "phone")
    op.drop_column("users", "email")
    op.drop_column("users", "phone")
