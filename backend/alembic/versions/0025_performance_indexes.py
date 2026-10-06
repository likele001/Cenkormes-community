"""add performance indexes for frequently queried columns

Identified missing indexes from query analysis:
- tasks.status: filtered by status in list/assign
- reports.status: filtered by status in audit workflow
- orders.status: filtered in order list
- work_orders.status: filtered in work order list
- reports.created_at: used in date-range queries (daily trend, dashboard)
- salary_items (user_id, month): used in monthly salary queries
- notifications (user_id, read_at): used in unread count and list
- operation_logs.created_at: used in sorted log listing

Revision ID: 0025_performance_indexes
Revises: 0024_task_equipment_id
"""

from alembic import op
from sqlalchemy import inspect


revision = "0025_performance_indexes"
down_revision = "0024_task_equipment_id"
branch_labels = None
depends_on = None


def _index_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    return {idx["name"] for idx in inspect(bind).get_indexes(table_name)}


def _create_index_if_missing(name: str, table_name: str, columns: list[str]) -> None:
    if name not in _index_names(table_name):
        op.create_index(name, table_name, columns)


def _drop_index_if_exists(name: str, table_name: str) -> None:
    if name in _index_names(table_name):
        op.drop_index(name, table_name=table_name)


def upgrade():
    _create_index_if_missing("ix_tasks_status", "tasks", ["status"])
    _create_index_if_missing("ix_tasks_assigned_user_id_status", "tasks", ["assigned_user_id", "status"])
    _create_index_if_missing("ix_reports_status", "reports", ["status"])
    _create_index_if_missing("ix_reports_created_at", "reports", ["created_at"])
    _create_index_if_missing("ix_reports_status_created_at", "reports", ["status", "created_at"])
    _create_index_if_missing("ix_orders_status", "orders", ["status"])
    _create_index_if_missing("ix_orders_customer_id_status", "orders", ["customer_id", "status"])
    _create_index_if_missing("ix_work_orders_status", "work_orders", ["status"])
    _create_index_if_missing("ix_work_orders_order_id_status", "work_orders", ["order_id", "status"])
    _create_index_if_missing("ix_salary_items_user_id_month", "salary_items", ["user_id", "month"])
    _create_index_if_missing("ix_salary_items_month", "salary_items", ["month"])
    _create_index_if_missing("ix_notifications_user_id_read_at", "notifications", ["user_id", "read_at"])
    _create_index_if_missing("ix_operation_logs_created_at", "operation_logs", ["created_at"])
    _create_index_if_missing("ix_operation_logs_tenant_id_created_at", "operation_logs", ["tenant_id", "created_at"])


def downgrade():
    _drop_index_if_exists("ix_tasks_status", "tasks")
    _drop_index_if_exists("ix_tasks_assigned_user_id_status", "tasks")
    _drop_index_if_exists("ix_reports_status", "reports")
    _drop_index_if_exists("ix_reports_created_at", "reports")
    _drop_index_if_exists("ix_reports_status_created_at", "reports")
    _drop_index_if_exists("ix_orders_status", "orders")
    _drop_index_if_exists("ix_orders_customer_id_status", "orders")
    _drop_index_if_exists("ix_work_orders_status", "work_orders")
    _drop_index_if_exists("ix_work_orders_order_id_status", "work_orders")
    _drop_index_if_exists("ix_salary_items_user_id_month", "salary_items")
    _drop_index_if_exists("ix_salary_items_month", "salary_items")
    _drop_index_if_exists("ix_notifications_user_id_read_at", "notifications")
    _drop_index_if_exists("ix_operation_logs_created_at", "operation_logs")
    _drop_index_if_exists("ix_operation_logs_tenant_id_created_at", "operation_logs")
