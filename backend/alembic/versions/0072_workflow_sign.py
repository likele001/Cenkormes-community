"""S2: approval_steps 增加会签/或签/条件配置列（幂等）

Revision ID: 0072_workflow_sign
Revises: 0071_workflow_engine
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0072_workflow_sign"
down_revision = "0071_workflow_engine"
branch_labels = None
depends_on = None


def _has_column(bind, table, column):
    cols = [c["name"] for c in inspect(bind).get_columns(table)]
    return column in cols


def upgrade() -> None:
    bind = op.get_bind()
    # 会签/或签模式：single / and（会签）/ or（或签）
    if not _has_column(bind, "approval_steps", "sign_mode"):
        op.add_column(
            "approval_steps",
            sa.Column("sign_mode", sa.String(16), nullable=False, server_default="single",
                      comment="审批模式 single=单人 / and=会签 / or=或签"),
        )
    # 条件规则（JSON）：{"expr": "amount>10000", "else_role": "director"}
    if not _has_column(bind, "approval_steps", "condition_rule"):
        op.add_column(
            "approval_steps",
            sa.Column("condition_rule", sa.JSON(), nullable=True,
                      comment="条件网关配置：{expr, else_role}, 命中走 approver_role, 否则 else_role/跳过"),
        )
    # 显式审批人（JSON 数组用户ID）；缺省按 approver_role 解析
    if not _has_column(bind, "approval_steps", "assignee_ids"):
        op.add_column(
            "approval_steps",
            sa.Column("assignee_ids", sa.JSON(), nullable=True,
                      comment="显式审批人 user_id 列表（会话/或签时展开为多个待办）"),
        )


def downgrade() -> None:
    pass