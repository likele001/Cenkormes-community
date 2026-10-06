"""workflow engine: approval_flows 扩展 + 实例/任务/轨迹表

S1：串行审批引擎。
- approval_flows 增加 xml_content / version / is_released（为 S3 bpmn-js 预留）
- 新增 approval_instances / approval_tasks / approval_records
幂等：字段与表均先检查存在性再操作，可安全重复执行。
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0071_workflow_engine'
down_revision = '0070_erp_modules'
branch_labels = None
depends_on = None


def _has_column(bind, table: str, column: str) -> bool:
    cols = {c["name"] for c in inspect(bind).get_columns(table)}
    return column in cols


def upgrade() -> None:
    bind = op.get_bind()

    # ============ approval_flows 扩展 ============
    if not _has_column(bind, "approval_flows", "xml_content"):
        op.add_column(
            "approval_flows",
            sa.Column("xml_content", sa.Text(), nullable=True, comment="bpmn-js 流程定义 BPMN 2.0 XML"),
        )
    if not _has_column(bind, "approval_flows", "version"):
        op.add_column(
            "approval_flows",
            sa.Column("version", sa.Integer(), nullable=False, server_default="1", comment="流程版本号"),
        )
    if not _has_column(bind, "approval_flows", "is_released"):
        op.add_column(
            "approval_flows",
            sa.Column("is_released", sa.Boolean(), nullable=False, server_default="0", comment="是否正式发布"),
        )

    # ============ approval_instances ============
    if not inspect(bind).has_table("approval_instances"):
        op.create_table(
            "approval_instances",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("flow_id", sa.Integer, sa.ForeignKey("approval_flows.id", ondelete="SET NULL"), nullable=True),
            sa.Column("flow_version", sa.Integer, nullable=False, server_default="1"),
            sa.Column("biz_type", sa.String(32), nullable=False),
            sa.Column("biz_id", sa.Integer, nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="running"),
            sa.Column("current_node", sa.String(64), nullable=True),
            sa.Column("initiator_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("meta", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            mysql_engine="InnoDB",
        )
        op.create_index("ix_approval_instances_tenant_id", "approval_instances", ["tenant_id"])
        op.create_index("ix_approval_instances_flow_id", "approval_instances", ["flow_id"])
        op.create_index("ix_approval_instances_biz_type", "approval_instances", ["biz_type"])
        op.create_index("ix_approval_instances_biz_id", "approval_instances", ["biz_id"])

    # ============ approval_tasks ============
    if not inspect(bind).has_table("approval_tasks"):
        op.create_table(
            "approval_tasks",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("instance_id", sa.Integer, sa.ForeignKey("approval_instances.id", ondelete="CASCADE"), nullable=False),
            sa.Column("step_order", sa.Integer, nullable=False, server_default="0"),
            sa.Column("node_key", sa.String(64), nullable=False),
            sa.Column("node_type", sa.String(32), nullable=False, server_default="userTask"),
            sa.Column("approver_role", sa.String(32), nullable=True),
            sa.Column("assignee_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("sign_mode", sa.String(16), nullable=False, server_default="single"),
            sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("deadline_at", sa.DateTime, nullable=True),
            sa.Column("operated_at", sa.DateTime, nullable=True),
            sa.Column("operated_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            mysql_engine="InnoDB",
        )
        op.create_index("ix_approval_tasks_tenant_id", "approval_tasks", ["tenant_id"])
        op.create_index("ix_approval_tasks_instance_id", "approval_tasks", ["instance_id"])
        op.create_index("ix_approval_tasks_status", "approval_tasks", ["status"])

    # ============ approval_records ============
    if not inspect(bind).has_table("approval_records"):
        op.create_table(
            "approval_records",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("instance_id", sa.Integer, sa.ForeignKey("approval_instances.id", ondelete="CASCADE"), nullable=False),
            sa.Column("task_id", sa.Integer, sa.ForeignKey("approval_tasks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("node_key", sa.String(64), nullable=True),
            sa.Column("action", sa.String(24), nullable=False),
            sa.Column("operator_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("operator_role", sa.String(32), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("from_user_id", sa.Integer, nullable=True),
            sa.Column("to_user_id", sa.Integer, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            mysql_engine="InnoDB",
        )
        op.create_index("ix_approval_records_tenant_id", "approval_records", ["tenant_id"])
        op.create_index("ix_approval_records_instance_id", "approval_records", ["instance_id"])


def downgrade() -> None:
    bind = op.get_bind()
    for tbl in ("approval_records", "approval_tasks", "approval_instances"):
        if inspect(bind).has_table(tbl):
            op.drop_table(tbl)
    for col in ("xml_content", "version", "is_released"):
        if _has_column(bind, "approval_flows", col):
            op.drop_column("approval_flows", col)