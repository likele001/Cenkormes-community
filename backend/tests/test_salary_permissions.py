"""工资/补贴权限拆分（P0-5）回归测试

背景：/reports/salary/*（明细/汇总/补贴）原整组挂 report.audit，
qc/班组长等角色可直接调 API 查看全厂工资、给任意员工添加补贴。

修复：
- 读端点（items/summary/allowances 列表）：salary.view 或 salary.manage
- 写端点（POST allowances）：salary.manage，且校验员工归属（同租户）

覆盖：
- 持有 report.audit（模拟 qc，无 salary 权限）→ 工资读写均 403（防回归）
- salary.view → 读 200、写 403
- salary.manage → 读 200、写本租户 200、写他租户/不存在 400
- report.audit 端点（报工列表）不受拆分影响
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.admin.production import reports as reports_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.tenant import Tenant
from app.models.user import User


@pytest.fixture()
def api(session, tenant, test_user):
    app = FastAPI()
    app.include_router(reports_module.router, prefix="/reports")
    app.include_router(reports_module.salary_router, prefix="/reports")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user

    def set_perms(codes: list[str]):
        app.dependency_overrides[get_current_permissions] = lambda: list(codes)

    set_perms([])
    return TestClient(app), set_perms


def _payload(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "allowance_type": "bonus",
        "amount": 100,
        "month": "2026-10",
        "reason": "测试补贴",
    }


def test_report_audit_only_cannot_access_salary(api, test_user):
    """只有 report.audit（模拟 qc）→ 工资读/写全部 403。"""
    client, set_perms = api
    set_perms(["report.audit"])
    assert client.get("/reports/salary/items").status_code == 403
    assert client.get("/reports/salary/summary").status_code == 403
    assert client.get("/reports/salary/allowances").status_code == 403
    assert client.post("/reports/salary/allowances", json=_payload(test_user.id)).status_code == 403


def test_no_permission_denied(api, test_user):
    """无任何权限 → 403。"""
    client, set_perms = api
    set_perms([])
    assert client.get("/reports/salary/items").status_code == 403
    assert client.post("/reports/salary/allowances", json=_payload(test_user.id)).status_code == 403


def test_salary_view_read_ok_write_forbidden(api, test_user):
    """salary.view：可读明细/汇总/补贴，但不可新增补贴。"""
    client, set_perms = api
    set_perms(["salary.view"])
    assert client.get("/reports/salary/items").status_code == 200
    assert client.get("/reports/salary/summary").status_code == 200
    assert client.get("/reports/salary/allowances").status_code == 200
    assert client.post("/reports/salary/allowances", json=_payload(test_user.id)).status_code == 403


def test_salary_manage_read_and_write(api, test_user):
    """salary.manage：可读（防能写不能读死角）且可写本租户员工补贴。"""
    client, set_perms = api
    set_perms(["salary.manage"])
    assert client.get("/reports/salary/items").status_code == 200
    r = client.post("/reports/salary/allowances", json=_payload(test_user.id))
    assert r.status_code == 200
    assert r.json()["data"]["amount"] == 100.0


def test_allowance_cross_tenant_user_rejected(api, session, test_user):
    """写他租户员工 / 不存在员工 → 400。"""
    client, set_perms = api
    set_perms(["salary.manage"])

    other = Tenant(code="OTH-SAL", name="他厂")
    session.add(other)
    session.flush()
    other_user = User(
        tenant_id=other.id, username="other_emp", password_hash="x",
        full_name="他厂员工", is_active=True,
    )
    session.add(other_user)
    session.flush()

    assert client.post("/reports/salary/allowances", json=_payload(other_user.id)).status_code == 400
    assert client.post("/reports/salary/allowances", json=_payload(999999)).status_code == 400


def test_report_audit_endpoints_unaffected(api):
    """拆分后 report.audit 端点（报工列表）仍可访问。"""
    client, set_perms = api
    set_perms(["report.audit"])
    assert client.get("/reports").status_code == 200
