"""老板看板指标数据基础

Revision ID: 0054_exec_dashboard_metrics
Revises: 99988930d734

老板看板 5 大指标需要的数据字段补充：
- orders 加 amount (销售额) + actual_completed_at (准交率)
- order_items 加 unit_price + subtotal (订单金额明细)
- skus 加 cost_price (毛利率)
- work_orders 加 standard_hours + actual_hours (产能利用率)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0054_exec_dashboard_metrics"
down_revision = "99988930d734"
branch_labels = None
depends_on = None


def _has_column(conn, table: str, column: str) -> bool:
    insp = inspect(conn)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade():
    conn = op.get_bind()

    # 1. orders：销售额 + 实际完成时间
    if not _has_column(conn, "orders", "amount"):
        op.add_column(
            "orders",
            sa.Column("amount", sa.Numeric(14, 2), nullable=False, server_default="0", comment="订单总金额（元）"),
        )
    if not _has_column(conn, "orders", "actual_completed_at"):
        op.add_column(
            "orders",
            sa.Column("actual_completed_at", sa.DateTime(), nullable=True, comment="实际完成时间"),
        )
    if not _has_column(conn, "orders", "cost_amount"):
        op.add_column(
            "orders",
            sa.Column("cost_amount", sa.Numeric(14, 2), nullable=False, server_default="0", comment="订单成本（元，毛利率计算）"),
        )

    # 2. order_items：单价 + 小计
    if not _has_column(conn, "order_items", "unit_price"):
        op.add_column(
            "order_items",
            sa.Column("unit_price", sa.Numeric(12, 4), nullable=False, server_default="0", comment="单价"),
        )
    if not _has_column(conn, "order_items", "subtotal"):
        op.add_column(
            "order_items",
            sa.Column("subtotal", sa.Numeric(14, 2), nullable=False, server_default="0", comment="小计金额"),
        )

    # 3. skus：成本价（毛利率）
    if not _has_column(conn, "skus", "cost_price"):
        op.add_column(
            "skus",
            sa.Column("cost_price", sa.Numeric(12, 4), nullable=False, server_default="0", comment="单位成本（元）"),
        )

    # 4. work_orders：标准工时 + 实际工时（产能利用率）
    if not _has_column(conn, "work_orders", "standard_hours"):
        op.add_column(
            "work_orders",
            sa.Column("standard_hours", sa.Numeric(10, 2), nullable=False, server_default="0", comment="标准工时"),
        )
    if not _has_column(conn, "work_orders", "actual_hours"):
        op.add_column(
            "work_orders",
            sa.Column("actual_hours", sa.Numeric(10, 2), nullable=False, server_default="0", comment="实际工时"),
        )
    if not _has_column(conn, "work_orders", "started_at"):
        op.add_column(
            "work_orders",
            sa.Column("started_at", sa.DateTime(), nullable=True, comment="实际开工时间"),
        )
    if not _has_column(conn, "work_orders", "finished_at"):
        op.add_column(
            "work_orders",
            sa.Column("finished_at", sa.DateTime(), nullable=True, comment="实际完工时间"),
        )

    # 5. 索引（按需）：用于老板看板聚合查询
    try:
        op.create_index("ix_orders_status_confirmed", "orders", ["status", "confirmed_at"])
    except Exception:
        pass
    try:
        op.create_index("ix_orders_actual_completed", "orders", ["actual_completed_at"])
    except Exception:
        pass


def downgrade():
    conn = op.get_bind()

    try:
        op.drop_index("ix_orders_actual_completed", table_name="orders")
    except Exception:
        pass
    try:
        op.drop_index("ix_orders_status_confirmed", table_name="orders")
    except Exception:
        pass

    if _has_column(conn, "work_orders", "finished_at"):
        op.drop_column("work_orders", "finished_at")
    if _has_column(conn, "work_orders", "started_at"):
        op.drop_column("work_orders", "started_at")
    if _has_column(conn, "work_orders", "actual_hours"):
        op.drop_column("work_orders", "actual_hours")
    if _has_column(conn, "work_orders", "standard_hours"):
        op.drop_column("work_orders", "standard_hours")

    if _has_column(conn, "skus", "cost_price"):
        op.drop_column("skus", "cost_price")

    if _has_column(conn, "order_items", "subtotal"):
        op.drop_column("order_items", "subtotal")
    if _has_column(conn, "order_items", "unit_price"):
        op.drop_column("order_items", "unit_price")

    if _has_column(conn, "orders", "cost_amount"):
        op.drop_column("orders", "cost_amount")
    if _has_column(conn, "orders", "actual_completed_at"):
        op.drop_column("orders", "actual_completed_at")
    if _has_column(conn, "orders", "amount"):
        op.drop_column("orders", "amount")