"""0074: 订单添加销售归属 sales_id，供应商添加归属人 owner_id

ABAC 行级过滤依赖这两个字段（销售只看自己名下订单/供应商）。
幂等：仅当列不存在时添加。
"""

import sqlalchemy as sa
from alembic import op

revision = "0074_add_business_owner_fields"
down_revision = "0073_abac_init"
branch_labels = None
depends_on = None


def _column_exists(bind, table, column) -> bool:
    rows = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
        ),
        {"t": table, "c": column},
    ).scalar()
    return bool(rows)


def _index_exists(bind, table, index) -> bool:
    rows = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND INDEX_NAME = :i"
        ),
        {"t": table, "i": index},
    ).scalar()
    return bool(rows)


def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "orders", "sales_id"):
        op.add_column(
            "orders",
            sa.Column(
                "sales_id",
                sa.Integer(),
                nullable=True,
                comment="销售归属人（ABAC 行级过滤字段）",
            ),
        )
    if not _index_exists(bind, "orders", "ix_orders_sales_id"):
        op.create_index("ix_orders_sales_id", "orders", ["sales_id"])

    if not _column_exists(bind, "suppliers", "owner_id"):
        op.add_column(
            "suppliers",
            sa.Column(
                "owner_id",
                sa.Integer(),
                nullable=True,
                comment="归属人（ABAC 行级过滤字段）",
            ),
        )
    if not _index_exists(bind, "suppliers", "ix_suppliers_owner_id"):
        op.create_index("ix_suppliers_owner_id", "suppliers", ["owner_id"])

    # 外键约束幂等（仅当不存在时添加）；KEY_COLUMN_USAGE 有 TABLE_SCHEMA 列
    def _fk_cols(table):
        rows = bind.execute(
            sa.text(
                "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t "
                "AND REFERENCED_TABLE_NAME = 'users' AND COLUMN_NAME = :c"
            ),
            {"t": table, "c": {"orders": "sales_id", "suppliers": "owner_id"}[table]},
        ).fetchall()
        return [r[0] for r in rows]

    if not _fk_cols("orders"):
        try:
            op.create_foreign_key(
                "fk_orders_sales_id", "orders", "users", ["sales_id"], ["id"], ondelete="SET NULL"
            )
        except Exception:
            pass  # 约束冲突时忽略（如已存在同列外键）

    if not _fk_cols("suppliers"):
        try:
            op.create_foreign_key(
                "fk_suppliers_owner_id", "suppliers", "users", ["owner_id"], ["id"], ondelete="SET NULL"
            )
        except Exception:
            pass


def downgrade() -> None:
    bind = op.get_bind()
    for table, col, fk in [
        ("orders", "sales_id", "fk_orders_sales_id"),
        ("suppliers", "owner_id", "fk_suppliers_owner_id"),
    ]:
        try:
            op.drop_constraint(fk, table, type_="foreignkey")
        except Exception:
            pass
        if _column_exists(bind, table, col):
            op.drop_column(table, col)