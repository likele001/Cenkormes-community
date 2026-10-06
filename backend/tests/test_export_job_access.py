"""导出任务访问控制（P2-18）回归测试

背景：`GET /admin/export-jobs/{id}` 仅 admin portal 登录即可按 id 读任意导出任务
（含薪资导出参数/结果附件），同租户普通管理端用户可越权读取敏感导出。

修复：创建者本人可读；非创建者需具备 job_type 对应业务权限码
（salary_excel→salary.manage、finance_statement→finance.manage、
purchase_statement→purchase.manage、warehouse_stock→warehouse.manage、
report_production/report_yield→report.view）；未知类型保守拒绝（fail-closed）。

覆盖：
- 创建者本人无任何业务权限也可读自己的任务
- 他人持有对应权限 → 可读；无对应权限 → 403
- 未知 job_type → 403（fail-closed）
- 跨租户 → 404（既有租户隔离不回归）
- report_production 用 report.view 权限可读
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.admin import export_jobs as export_jobs_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.export_job import ExportJob
from app.models.tenant import Tenant
from app.models.user import User


@pytest.fixture()
def owner(session, tenant) -> User:
    u = User(tenant_id=tenant.id, username="owner1", password_hash="x", full_name="导出发起人", is_active=True)
    session.add(u)
    session.flush()
    return u


@pytest.fixture()
def other(session, tenant) -> User:
    u = User(tenant_id=tenant.id, username="other1", password_hash="x", full_name="其他用户", is_active=True)
    session.add(u)
    session.flush()
    return u


@pytest.fixture()
def api(session, other):
    app = FastAPI()
    app.include_router(export_jobs_module.router, prefix="/admin")
    holder = {"user": other, "perms": []}
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: holder["user"]
    app.dependency_overrides[get_current_permissions] = lambda: holder["perms"]
    client = TestClient(app)
    client.holder = holder
    return client


def _mk_job(session, tenant_id: int, created_by: int, job_type: str = "salary_excel") -> ExportJob:
    job = ExportJob(tenant_id=tenant_id, job_type=job_type, created_by=created_by, params_json='{"month":"2026-09"}')
    session.add(job)
    session.flush()
    return job


def test_owner_reads_own_job(api, session, tenant, owner):
    """创建者本人：无需业务权限即可读自己的任务。"""
    job = _mk_job(session, tenant.id, owner.id)
    api.holder["user"] = owner
    api.holder["perms"] = []
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 200, r.text
    assert r.json()["data"]["job_type"] == "salary_excel"


def test_other_with_permission_allowed(api, session, tenant, owner, other):
    """非创建者持有对应权限（salary.manage）→ 可读。"""
    job = _mk_job(session, tenant.id, owner.id)
    api.holder["perms"] = ["salary.manage"]
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 200, r.text


def test_other_without_permission_rejected(api, session, tenant, owner, other):
    """非创建者无对应权限 → 403（不泄漏任务内容）。"""
    job = _mk_job(session, tenant.id, owner.id)
    api.holder["perms"] = ["report.view"]
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 403


def test_unknown_job_type_rejected(api, session, tenant, owner):
    """未知 job_type：即使持有部分权限也保守拒绝（fail-closed）。"""
    job = _mk_job(session, tenant.id, owner.id, job_type="mystery_export")
    api.holder["perms"] = ["salary.manage", "finance.manage", "warehouse.manage"]
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 403


def test_cross_tenant_404(api, session, tenant, owner):
    """跨租户任务 → 404（租户隔离不回归）。"""
    other_tenant = Tenant(code="OTX", name="他厂X")
    session.add(other_tenant)
    session.flush()
    other_owner = User(tenant_id=other_tenant.id, username="oth", password_hash="x", is_active=True)
    session.add(other_owner)
    session.flush()
    job = _mk_job(session, other_tenant.id, other_owner.id)
    api.holder["perms"] = ["salary.manage"]
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 404


def test_report_job_with_view_permission(api, session, tenant, owner):
    """report_production 对应 report.view 权限可读。"""
    job = _mk_job(session, tenant.id, owner.id, job_type="report_production")
    api.holder["perms"] = ["report.view"]
    r = api.get(f"/admin/export-jobs/{job.id}")
    assert r.status_code == 200, r.text
