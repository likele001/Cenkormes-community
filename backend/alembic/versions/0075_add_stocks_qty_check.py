"""0075: stocks.qty 非负 CHECK 约束

幂等：约束已存在则跳过；数据库不支持（MySQL < 8.0.16）或存量负数数据
导致添加失败时告警跳过——应用层已有非负护栏（crud/warehouse.adjust_stock）。
"""

import logging

import sqlalchemy as sa
from alembic import op

revision = "0075_add_stocks_qty_check"
down_revision = "0074_add_business_owner_fields"
branch_labels = None
depends_on = None

logger = logging.getLogger("alembic.runtime.migration")


def _constraint_exists(bind) -> bool:
    rows = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stocks' "
            "AND CONSTRAINT_NAME = 'ck_stocks_qty_nonneg'"
        )
    ).scalar()
    return bool(rows)


def upgrade() -> None:
    bind = op.get_bind()
    try:
        if _constraint_exists(bind):
            return
        op.create_check_constraint("ck_stocks_qty_nonneg", "stocks", "qty >= 0")
    except Exception as e:  # noqa: BLE001 —— 不阻断部署
        logger.warning("skip ck_stocks_qty_nonneg (existing negative data or unsupported): %s", e)


def downgrade() -> None:
    bind = op.get_bind()
    try:
        if _constraint_exists(bind):
            op.drop_constraint("ck_stocks_qty_nonneg", "stocks", type_="check")
    except Exception:  # noqa: BLE001
        pass
