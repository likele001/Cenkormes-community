"""CRM-MES 闭环：客户负责人、商机关联订单、跟进提醒

Revision ID: 0049_crm_mes_loop
Revises: 0048_push_retry_alert
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0049_crm_mes_loop"
down_revision = "0048_push_retry_alert"
branch_labels = None
depends_on = None


def _has_column(conn, table: str, column: str) -> bool:
    insp = inspect(conn)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade():
    conn = op.get_bind()

    if not _has_column(conn, "orders", "opportunity_id"):
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
            pass

    if not _has_column(conn, "customers", "owner_user_id"):
        op.add_column("customers", sa.Column("owner_user_id", sa.Integer(), nullable=True))
        op.create_index("ix_customers_owner_user_id", "customers", ["owner_user_id"], unique=False)
        try:
            op.create_foreign_key(
                "fk_customers_owner_user_id",
                "customers",
                "users",
                ["owner_user_id"],
                ["id"],
                ondelete="SET NULL",
            )
        except Exception:
            pass

    if not _has_column(conn, "crm_opportunity_activities", "next_follow_up_at"):
        op.add_column("crm_opportunity_activities", sa.Column("next_follow_up_at", sa.DateTime(), nullable=True))

    if not _has_column(conn, "crm_opportunities", "converted_order_id"):
        op.add_column("crm_opportunities", sa.Column("converted_order_id", sa.Integer(), nullable=True))
        op.create_index("ix_crm_opportunities_converted_order_id", "crm_opportunities", ["converted_order_id"], unique=False)
        try:
            op.create_foreign_key(
                "fk_crm_opportunities_converted_order_id",
                "crm_opportunities",
                "orders",
                ["converted_order_id"],
                ["id"],
                ondelete="SET NULL",
            )
        except Exception:
            pass


def downgrade():
    conn = op.get_bind()

    if _has_column(conn, "crm_opportunities", "converted_order_id"):
        try:
            op.drop_constraint("fk_crm_opportunities_converted_order_id", "crm_opportunities", type_="foreignkey")
        except Exception:
            pass
        try:
            op.drop_index("ix_crm_opportunities_converted_order_id", table_name="crm_opportunities")
        except Exception:
            pass
        op.drop_column("crm_opportunities", "converted_order_id")

    if _has_column(conn, "crm_opportunity_activities", "next_follow_up_at"):
        op.drop_column("crm_opportunity_activities", "next_follow_up_at")

    if _has_column(conn, "customers", "owner_user_id"):
        try:
            op.drop_constraint("fk_customers_owner_user_id", "customers", type_="foreignkey")
        except Exception:
            pass
        try:
            op.drop_index("ix_customers_owner_user_id", table_name="customers")
        except Exception:
            pass
        op.drop_column("customers", "owner_user_id")

    if _has_column(conn, "orders", "opportunity_id"):
        try:
            op.drop_constraint("fk_orders_opportunity_id", "orders", type_="foreignkey")
        except Exception:
            pass
        try:
            op.drop_index("ix_orders_opportunity_id", table_name="orders")
        except Exception:
            pass
        op.drop_column("orders", "opportunity_id")
