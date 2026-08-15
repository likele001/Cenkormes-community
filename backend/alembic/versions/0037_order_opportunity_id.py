"""orders 关联 CRM 商机（补回服务器已执行但仓库缺失的迁移）

Revision ID: 0037_order_opportunity_id
Revises: 0036_wechat_miniapp
Create Date: 2026-05-25

说明：部分环境 alembic_version 已为 0037，但代码库曾缺此文件会导致
`Can't locate revision identified by '0037_order_opportunity_id'`。
本脚本对未建列的环境补列；已存在则跳过。
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0037_order_opportunity_id"
down_revision = "0036_wechat_miniapp"
branch_labels = None
depends_on = None


def _orders_has_opportunity_id(conn) -> bool:
    insp = inspect(conn)
    if "orders" not in insp.get_table_names():
        return False
    return any(c["name"] == "opportunity_id" for c in insp.get_columns("orders"))


def upgrade():
    conn = op.get_bind()
    if _orders_has_opportunity_id(conn):
        return
    op.add_column("orders", sa.Column("opportunity_id", sa.Integer(), nullable=True))
    op.create_index("ix_orders_opportunity_id", "orders", ["opportunity_id"], unique=False)
    try:
        op.create_foreign_key(
            "fk_orders_opportunity_id",
            "orders",
            "crm_opportunities",
            ["opportunity_id"],
            ["id"],
            ondelete="SET NULL",
        )
    except Exception:
        # 表名或约束已存在时忽略
        pass


def downgrade():
    conn = op.get_bind()
    if not _orders_has_opportunity_id(conn):
        return
    try:
        op.drop_constraint("fk_orders_opportunity_id", "orders", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_index("ix_orders_opportunity_id", table_name="orders")
    except Exception:
        pass
    op.drop_column("orders", "opportunity_id")
