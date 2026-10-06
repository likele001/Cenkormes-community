"""0076: statements 表增加客户回款登记字段

P1-7：客户在 H5 自助提交「回款登记」（payment_submitted_at/remark），
仅记录申报信息并通知财务核实，不再由客户直接置 paid / 记收入流水。
幂等：列已存在则跳过。
"""

import sqlalchemy as sa
from alembic import op

revision = "0076_stmt_payment_submit"
down_revision = "0075_add_stocks_qty_check"
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


def upgrade() -> None:
    bind = op.get_bind()
    cols = [
        ("payment_submitted_at", sa.DateTime(), "客户提交回款登记时间"),
        ("payment_submitted_remark", sa.String(255), "客户回款登记备注"),
    ]
    for name, coltype, comment in cols:
        if _column_exists(bind, "statements", name):
            continue
        op.add_column("statements", sa.Column(name, coltype, nullable=True, comment=comment))


def downgrade() -> None:
    bind = op.get_bind()
    for name in ("payment_submitted_at", "payment_submitted_remark"):
        if _column_exists(bind, "statements", name):
            op.drop_column("statements", name)
