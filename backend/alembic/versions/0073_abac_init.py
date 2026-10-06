"""S3: ABAC 权限表初始化（幂等）

创建 data_scopes / policy_rules / policy_bindings / field_policies 四张表。
幂等：已存在的表跳过，不报错（可重复执行）。
附带写入系统内置数据范围字典（ALL / DEPT_SUBTREE / DEPT / WORKSHOP / SELF），
仅当该租户尚无对应 code 时才插入。

Revision ID: 0073_abac_init
Revises: 0072_workflow_sign
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0073_abac_init"
down_revision = "0072_workflow_sign"
branch_labels = None
depends_on = None


def _table_exists(bind, table):
    return sa.inspect(bind).has_table(table)


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "data_scopes"):
        op.create_table(
            "data_scopes",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(32), nullable=False),
            sa.Column("name", sa.String(64), nullable=False),
            sa.Column("description", sa.String(255), nullable=True),
            sa.Column("scope_type", sa.String(32), nullable=False),
            sa.Column("expr", sa.String(512), nullable=True),
            sa.Column("is_system", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "code", name="uq_data_scopes_tenant_code"),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        op.create_index("ix_data_scopes_tenant", "data_scopes", ["tenant_id"])
        op.create_index("ix_data_scopes_tenant_is_system", "data_scopes", ["tenant_id", "is_system"])

    if not _table_exists(bind, "policy_rules"):
        op.create_table(
            "policy_rules",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("resource", sa.String(64), nullable=False),
            sa.Column("role_code", sa.String(64), nullable=False),
            sa.Column("row_filter_scope", sa.String(32), nullable=True),
            sa.Column("column_mask_json", sa.JSON(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "resource", "role_code", name="uq_policy_rules_tenant_res_role"),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        op.create_index("ix_policy_rules_tenant_res", "policy_rules", ["tenant_id", "resource"])
        op.create_index("ix_policy_rules_tenant_res_active", "policy_rules", ["tenant_id", "resource", "is_active"])

    if not _table_exists(bind, "policy_bindings"):
        op.create_table(
            "policy_bindings",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("principal_type", sa.String(16), nullable=False),
            sa.Column("principal_id", sa.Integer(), nullable=False),
            sa.Column("resource", sa.String(64), nullable=False),
            sa.Column("scope_code", sa.String(32), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "principal_type", "principal_id", "resource", name="uq_policy_bindings_tenant_principal_res"),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        op.create_index("ix_policy_bindings_tenant_res_principal", "policy_bindings", ["tenant_id", "resource", "principal_id"])

    if not _table_exists(bind, "field_policies"):
        op.create_table(
            "field_policies",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("resource", sa.String(64), nullable=False),
            sa.Column("field_name", sa.String(64), nullable=False),
            sa.Column("role_code", sa.String(64), nullable=False),
            sa.Column("mask_type", sa.String(16), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "resource", "field_name", "role_code", name="uq_field_policies_tenant_res_field_role"),
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
        )
        op.create_index("ix_field_policies_tenant_res", "field_policies", ["tenant_id", "resource"])

    # 系统内置数据范围字典：为每个已有租户插入内置范围（缺失才插，幂等）
    tenants = bind.execute(sa.text("SELECT id FROM tenants")).fetchall() if _table_exists(bind, "tenants") else []
    builtins = [
        ("ALL", "全公司", "ALL", "可访问全部数据（通常用于管理员）"),
        ("DEPT_SUBTREE", "本部门及下级", "DEPT_SUBTREE", "本部门及所有下级部门数据"),
        ("DEPT", "本部门", "DEPT", "仅本部门数据"),
        ("WORKSHOP", "本车间", "WORKSHOP", "仅本车间数据"),
        ("SELF", "本人", "SELF", "仅本人创建/负责的数据"),
    ]
    for (tid,) in tenants:
        for code, name, scope_type, desc in builtins:
            exists = bind.execute(
                sa.text("SELECT 1 FROM data_scopes WHERE tenant_id=:t AND code=:c"),
                {"t": tid, "c": code},
            ).first()
            if not exists:
                bind.execute(
                    sa.text(
                        "INSERT INTO data_scopes (tenant_id, code, name, description, scope_type, is_system) "
                        "VALUES (:t, :c, :n, :d, :s, 1)"
                    ),
                    {"t": tid, "c": code, "n": name, "d": desc, "s": scope_type},
                )


def downgrade() -> None:
    # 幂等：downgrade 仅删除 ABAC 相关表（若存在），并移除内置范围
    bind = op.get_bind()
    for table in ("field_policies", "policy_bindings", "policy_rules", "data_scopes"):
        if _table_exists(bind, table):
            op.drop_table(table)