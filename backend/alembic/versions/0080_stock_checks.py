"""stock_checks / stock_check_items：库存盘点单（P2-21）

- stock_checks：盘点单（draft 录入中 → done 已完成），快照建单
- stock_check_items：账面快照 book_qty → 实盘 actual_qty → diff_qty；
  完成时 diff≠0 的行调整 stocks 并写 stock_logs(stock_check) 流水。

幂等：表已存在则跳过。revision id 须 ≤32 字符（alembic_version.version_num VARCHAR(32)）。
"""

import sqlalchemy as sa
from alembic import op

revision = "0080_stock_checks"
down_revision = "0079_statement_payments"
branch_labels = None
depends_on = None


def _table_exists(bind, table: str) -> bool:
    rows = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
        ),
        {"t": table},
    ).scalar()
    return bool(rows)


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "stock_checks"):
        op.create_table(
            "stock_checks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(32), nullable=False, comment="盘点单号"),
            sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False),
            sa.Column("check_date", sa.Date(), nullable=False, comment="盘点日期"),
            sa.Column("status", sa.String(16), nullable=False, server_default="draft", comment="draft 录入中 / done 已完成"),
            sa.Column("remark", sa.String(255), nullable=True),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("tenant_id", "code", name="uq_stock_checks_tenant_code"),
        )
        op.create_index("ix_stock_checks_tenant_id", "stock_checks", ["tenant_id"])
        op.create_index("ix_stock_checks_warehouse_id", "stock_checks", ["warehouse_id"])
        op.create_index("ix_stock_checks_created_by", "stock_checks", ["created_by"])
    if not _table_exists(bind, "stock_check_items"):
        op.create_table(
            "stock_check_items",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("check_id", sa.Integer(), sa.ForeignKey("stock_checks.id", ondelete="CASCADE"), nullable=False),
            sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("book_qty", sa.Integer(), nullable=False, comment="账面快照数量"),
            sa.Column("actual_qty", sa.Integer(), nullable=True, comment="实盘数量（未录入为 NULL）"),
            sa.Column("diff_qty", sa.Integer(), nullable=True, comment="差异 = 实盘 - 账面（完成时写入）"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("check_id", "sku_id", name="uq_stock_check_items_check_sku"),
        )
        op.create_index("ix_stock_check_items_tenant_id", "stock_check_items", ["tenant_id"])
        op.create_index("ix_stock_check_items_check_id", "stock_check_items", ["check_id"])
        op.create_index("ix_stock_check_items_sku_id", "stock_check_items", ["sku_id"])


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "stock_check_items"):
        op.drop_table("stock_check_items")
    if _table_exists(bind, "stock_checks"):
        op.drop_table("stock_checks")
