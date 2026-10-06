"""0079: 对账单核销记录表 + due_date（P1-10）

- statement_payments：逐笔收款/部分收款核销记录（customer/supplier 通用）
- statements.due_date / supplier_statements.due_date：账龄计算基准
  （基准日 = due_date，未设置时回退 period_end/period_to）

幂等：表/列已存在则跳过。revision id 须 ≤32 字符（alembic_version.version_num VARCHAR(32)）。
"""

import sqlalchemy as sa
from alembic import op

revision = "0079_statement_payments"
down_revision = "0078_salary_slip_pay"
branch_labels = None
depends_on = None


def _column_exists(bind, table: str, column: str) -> bool:
    rows = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
        ),
        {"t": table, "c": column},
    ).scalar()
    return bool(rows)


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
    if not _table_exists(bind, "statement_payments"):
        op.create_table(
            "statement_payments",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("statement_type", sa.String(16), nullable=False),
            sa.Column("statement_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Numeric(14, 4), nullable=False),
            sa.Column("biz_date", sa.Date(), nullable=False),
            sa.Column("method", sa.String(32), nullable=True),
            sa.Column("remark", sa.String(255), nullable=True),
            sa.Column("ledger_id", sa.Integer(), sa.ForeignKey("finance_ledgers.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_statement_payments_tenant_id", "statement_payments", ["tenant_id"])
        op.create_index("ix_statement_payments_created_by", "statement_payments", ["created_by"])
        op.create_index(
            "ix_statement_payments_biz", "statement_payments", ["tenant_id", "statement_type", "statement_id"]
        )
    for table in ("statements", "supplier_statements"):
        if not _column_exists(bind, table, "due_date"):
            op.add_column(table, sa.Column("due_date", sa.Date(), nullable=True, comment="约定到期日（账龄基准）"))


def downgrade() -> None:
    bind = op.get_bind()
    for table in ("statements", "supplier_statements"):
        if _column_exists(bind, table, "due_date"):
            op.drop_column(table, "due_date")
    if _table_exists(bind, "statement_payments"):
        op.drop_table("statement_payments")
