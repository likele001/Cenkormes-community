"""成品码：首工序赋码，全工序共用 product_code

Revision ID: 0035_product_code
Revises: 0034_process_flow
"""

from alembic import op
import sqlalchemy as sa


revision = "0035_product_code"
down_revision = "0034_process_flow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "work_order_pieces",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column("work_order_pieces", sa.Column("product_code", sa.String(length=64), nullable=True))
    op.add_column("work_order_pieces", sa.Column("last_process_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_work_order_pieces_last_process_id",
        "work_order_pieces",
        "processes",
        ["last_process_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_work_order_pieces_product_code", "work_order_pieces", ["product_code"])
    op.create_unique_constraint(
        "uq_work_order_pieces_tenant_product_code",
        "work_order_pieces",
        ["tenant_id", "product_code"],
    )

    op.add_column("trace_codes", sa.Column("product_code", sa.String(length=64), nullable=True))
    op.create_index("ix_trace_codes_product_code", "trace_codes", ["product_code"])


def downgrade() -> None:
    op.drop_index("ix_trace_codes_product_code", table_name="trace_codes")
    op.drop_column("trace_codes", "product_code")

    op.drop_constraint("uq_work_order_pieces_tenant_product_code", "work_order_pieces", type_="unique")
    op.drop_index("ix_work_order_pieces_product_code", table_name="work_order_pieces")
    op.drop_constraint("fk_work_order_pieces_last_process_id", "work_order_pieces", type_="foreignkey")
    op.drop_column("work_order_pieces", "last_process_id")
    op.drop_column("work_order_pieces", "product_code")
