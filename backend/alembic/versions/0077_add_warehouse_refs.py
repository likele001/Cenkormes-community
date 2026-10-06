"""0077: 发货/外协发料收回补仓库引用

P1-8：库存责任可追溯——
- shipments.warehouse_id：发货单显式指定发货仓库（NULL=历史单据，发货时回退默认仓并回写）
- subcontract_send_logs.warehouse_id：外协发料出库仓库（NULL=仅台账登记，未动库存）
- subcontract_receive_logs.warehouse_id：外协收回入库仓库（NULL=仅台账登记，未动库存）

幂等：列已存在则跳过。
"""

import sqlalchemy as sa
from alembic import op

revision = "0077_add_warehouse_refs"
down_revision = "0076_stmt_payment_submit"
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
    ("shipments", "warehouse_id", "发货仓库（NULL=历史单据，发货时回退默认仓）"),
    ("subcontract_send_logs", "warehouse_id", "发料出库仓库（NULL=仅台账登记）"),
    ("subcontract_receive_logs", "warehouse_id", "收回入库仓库（NULL=仅台账登记）"),
]


def upgrade() -> None:
    bind = op.get_bind()
    for table, name, comment in _COLS:
        if _column_exists(bind, table, name):
            continue
        op.add_column(table, sa.Column(name, sa.Integer(), nullable=True, comment=comment))


def downgrade() -> None:
    bind = op.get_bind()
    for table, name, _ in _COLS:
        if _column_exists(bind, table, name):
            op.drop_column(table, name)
