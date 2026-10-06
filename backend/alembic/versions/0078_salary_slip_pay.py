"""0078: salary_slips 增加发放字段

P1-9：工资发放落账——
- pay_status / paid_at / paid_by / pay_method：发放动作落库
- 发放时写 FinanceLedger(direction=out, category=labor, statement_type=salary_slip)
  使人工成本进入现金流与利润口径

幂等：列已存在则跳过。revision id 须 ≤32 字符（alembic_version.version_num VARCHAR(32)）。
"""

import sqlalchemy as sa
from alembic import op

revision = "0078_salary_slip_pay"
down_revision = "0077_add_warehouse_refs"
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


_COLS = [
    ("pay_status", sa.String(16), "发放状态 unpaid/paid"),
    ("paid_at", sa.DateTime(), "发放时间"),
    ("paid_by", sa.Integer(), "发放操作人"),
    ("pay_method", sa.String(32), "发放方式 cash/bank/wechat/alipay/other"),
]


def upgrade() -> None:
    bind = op.get_bind()
    for name, coltype, comment in _COLS:
        if _column_exists(bind, "salary_slips", name):
            continue
        op.add_column("salary_slips", sa.Column(name, coltype, nullable=True, comment=comment))
    # pay_status 业务上 NOT NULL，回填默认值（先加可空列再加默认，兼容存量行）
    op.execute("UPDATE salary_slips SET pay_status = 'unpaid' WHERE pay_status IS NULL")
    try:
        op.alter_column("salary_slips", "pay_status", existing_type=sa.String(16), nullable=False, server_default="unpaid")
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    for name, _, _ in reversed(_COLS):
        if _column_exists(bind, "salary_slips", name):
            op.drop_column("salary_slips", name)
