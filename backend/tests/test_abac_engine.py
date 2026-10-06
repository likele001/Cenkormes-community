# SPDX-License-Identifier: AGPL-3.0
"""ABAC 引擎 field_mask 合并逻辑与脱敏策略单元测试。

覆盖:
- 空角色 / 超级用户 fast-path
- policy_rules.column_mask_json 与 field_policies 两来源合并
- 通配角色码(@all/*)作为默认, 具体角色码覆盖通配
- FieldPolicy 同样支持通配 -> 具体 覆盖
- is_active 过滤
- 各掩码类型 NULL/FULL/LAST4/HASH
- mask_row / mask_rows 应用
"""
from __future__ import annotations

import pytest

from sqlalchemy import select

from app.models.abac import DataScope, FieldPolicy, PolicyRule
from app.models.user import User
from app.models.role import Role
from app.services.abac.engine import (
    AbacContext,
    AbacEngine,
    abac,
)


@pytest.fixture
def scope_all(session, tenant) -> DataScope:
    s = DataScope(tenant_id=tenant.id, code="ALL", name="全公司", scope_type="ALL", is_system=True)
    session.add(s)
    session.flush()
    return s


def make_engine(session, tenant, roles, *, user_id=1, is_superuser=False) -> AbacEngine:
    return AbacEngine(
        session,
        AbacContext(
            tenant_id=tenant.id,
            user_id=user_id,
            department_id=None,
            workshop_id=None,
            role_codes=list(roles),
            is_superuser=is_superuser,
        ),
    )


def add_policy_rule(session, tenant, *, resource, role_code, mask=None, active=True, priority=0):
    r = PolicyRule(
        tenant_id=tenant.id,
        resource=resource,
        role_code=role_code,
        row_filter_scope=None,
        column_mask_json=mask,
        is_active=active,
        priority=priority,
    )
    session.add(r)
    session.flush()
    return r


def add_field_policy(session, tenant, *, resource, field_name, role_code, mask_type, active=True):
    fp = FieldPolicy(
        tenant_id=tenant.id,
        resource=resource,
        field_name=field_name,
        role_code=role_code,
        mask_type=mask_type,
        is_active=active,
    )
    session.add(fp)
    session.flush()
    return fp


# ---------- fast-path ----------

def test_no_roles_returns_empty(session, tenant):
    eng = make_engine(session, tenant, [])
    assert eng.field_mask("customers") == {}


def test_superuser_returns_empty(session, tenant):
    eng = make_engine(session, tenant, ["employee"], is_superuser=True)
    add_policy_rule(session, tenant, resource="customers", role_code="@all", mask={"phone": "FULL"})
    assert eng.field_mask("customers") == {}


# ---------- policy_rules.column_mask_json ----------

def test_policy_rule_column_mask_applied(session, tenant):
    eng = make_engine(session, tenant, ["sales"])
    add_policy_rule(session, tenant, resource="customers", role_code="sales", mask={"phone": "LAST4", "email": "FULL"})
    assert eng.field_mask("customers") == {"phone": "LAST4", "email": "FULL"}


def test_wildcard_used_when_no_specific(session, tenant):
    eng = make_engine(session, tenant, ["sales"])
    add_policy_rule(session, tenant, resource="customers", role_code="@all", mask={"phone": "FULL"})
    assert eng.field_mask("customers") == {"phone": "FULL"}


def test_specific_role_overrides_wildcard(session, tenant):
    eng = make_engine(session, tenant, ["sales"])
    add_policy_rule(session, tenant, resource="customers", role_code="@all", mask={"phone": "FULL", "email": "HASH"})
    add_policy_rule(session, tenant, resource="customers", role_code="sales", mask={"phone": "LAST4"})
    masked = eng.field_mask("customers")
    # sales 具体规则覆盖通配的 phone; email 未被覆盖, 保留通配
    assert masked["phone"] == "LAST4"
    assert masked["email"] == "HASH"


def test_multiple_roles_merged(session, tenant):
    eng = make_engine(session, tenant, ["sales", "operator"])
    add_policy_rule(session, tenant, resource="customers", role_code="sales", mask={"phone": "LAST4"})
    add_policy_rule(session, tenant, resource="customers", role_code="operator", mask={"email": "FULL"})
    assert eng.field_mask("customers") == {"phone": "LAST4", "email": "FULL"}


def test_inactive_policy_rule_ignored(session, tenant):
    eng = make_engine(session, tenant, ["sales"])
    add_policy_rule(session, tenant, resource="customers", role_code="sales", mask={"phone": "LAST4"}, active=False)
    assert eng.field_mask("customers") == {}


def test_wildcard_both_forms_are_wild(session, tenant):
    eng = make_engine(session, tenant, ["sales"])
    add_policy_rule(session, tenant, resource="customers", role_code="*", mask={"a": "FULL"})
    add_policy_rule(session, tenant, resource="customers", role_code="@all", mask={"b": "HASH"})
    masked = eng.field_mask("customers")
    assert masked["a"] == "FULL"
    assert masked["b"] == "HASH"


# ---------- field_policies + 合并 ----------

def test_merge_policy_rule_and_field_policy(session, tenant):
    eng = make_engine(session, tenant, ["finance"])
    add_policy_rule(session, tenant, resource="salary_slips", role_code="finance", mask={"base": "FULL"})
    add_field_policy(session, tenant, resource="salary_slips", field_name="net_amount", role_code="finance", mask_type="NULL")
    masked = eng.field_mask("salary_slips")
    assert masked["base"] == "FULL"
    assert masked["net_amount"] == "NULL"


def test_field_policy_specific_overrides_policy_rule_wildcard(session, tenant):
    eng = make_engine(session, tenant, ["employee"])
    add_policy_rule(session, tenant, resource="salary_slips", role_code="@all", mask={"net_amount": "HASH"})
    add_field_policy(session, tenant, resource="salary_slips", field_name="net_amount", role_code="employee", mask_type="FULL")
    assert eng.field_mask("salary_slips")["net_amount"] == "FULL"


def test_field_policy_wildcard_default(session, tenant):
    eng = make_engine(session, tenant, ["employee"])
    add_field_policy(session, tenant, resource="salary_slips", field_name="id_card", role_code="@all", mask_type="LAST4")
    assert eng.field_mask("salary_slips")["id_card"] == "LAST4"


def test_inactive_field_policy_ignored(session, tenant):
    eng = make_engine(session, tenant, ["employee"])
    add_field_policy(session, tenant, resource="salary_slips", field_name="id_card", role_code="@all", mask_type="LAST4", active=False)
    assert eng.field_mask("salary_slips") == {}


# ---------- 掩码策略 ----------

def test_mask_value_types(session, tenant):
    eng = make_engine(session, tenant, ["employee"])
    assert eng.mask_value("NULL", "123456") is None
    assert eng.mask_value("NULL", None) is None
    assert eng.mask_value("FULL", "abcd") == "****"
    assert eng.mask_value("LAST4", "13800138000") == "*******8000"
    assert eng.mask_value("LAST4", "ab") == "**"
    assert eng.mask_value("HASH", "13800138000") == "0b6d2a80" or len(eng.mask_value("HASH", "13800138000")) == 8


def test_mask_row_applies(session, tenant):
    eng = make_engine(session, tenant, ["finance"])
    add_policy_rule(session, tenant, resource="salary_slips", role_code="finance", mask={"net_amount": "NULL", "base": "LAST4"})
    row = {"net_amount": 10000, "base": "13800138000", "bonus": 500}
    out = eng.mask_row("salary_slips", row)
    assert out["net_amount"] is None
    assert out["base"] == "*******8000"
    assert out["bonus"] == 500  # 未在规则中的字段保留


def test_mask_rows_applies_all(session, tenant):
    eng = make_engine(session, tenant, ["finance"])
    add_field_policy(session, tenant, resource="salary_slips", field_name="net_amount", role_code="finance", mask_type="NULL")
    rows = [{"net_amount": 100, "id": 1}, {"net_amount": 200, "id": 2}]
    out = eng.mask_rows("salary_slips", rows)
    assert out[0]["net_amount"] is None
    assert out[1]["net_amount"] is None


def test_mask_no_rule_no_change(session, tenant):
    eng = make_engine(session, tenant, ["finance"])
    row = {"net_amount": 100, "id": 1}
    assert eng.mask_row("salary_slips", row) == row