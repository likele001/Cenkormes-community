"""审核职责分离（SoD）（P1-13）回归测试

背景：报工审核无职责分离（审计 Part 1 #12/#13）：
- 审核人可审核本人提交的报工（自报自审，工资/绩效自我闭环）；
- 同一人可既初审又终审（两级审核形同虚设）；
- 临时报工"绑定即终审"同样可自绑，绕过审核监督。

修复：
- `assert_report_audit_sod` / `assert_unit_audit_sod`（crud 层公共校验）：
  所有审核动作（通过/驳回）拦截自审；终审/多级审核拦截与已审核人同人；
- 覆盖 4 条通道：admin 报工端点、件次端点、IM 卡片（飞书/钉钉）、企微卡片；
- 临时报工绑定（视为终审）补自审拦截。

覆盖：
- 自审：报工初审 / 终审 / 驳回、件次审核 / 驳回、临时绑定 均 400
- IM 卡片 / 企微卡片服务层自审抛对应错误
- 初审/终审同人：同一人终审 400，换人终审 200（两级留痕完整）
- 件次多级：同一人审两级 400
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.production import reports as reports_module
from app.api.admin.production import report_units as units_module
from app.api.admin.production import temp_reports as temp_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.order import Order, OrderItem
from app.models.report import Report, ReportAudit
from app.models.report_unit import ReportUnit
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.temp_report import TempReport
from app.models.user import User, user_roles
from app.models.work_order import WorkOrder


@pytest.fixture()
def worker(tenant, employee_role, session):
    u = User(tenant_id=tenant.id, username="worker1", password_hash="x", full_name="张员工", is_active=True)
    session.add(u)
    session.flush()
    session.execute(user_roles.insert().values(user_id=u.id, role_id=employee_role.id))
    session.flush()
    return u


@pytest.fixture()
def auditor2(tenant, admin_role, session):
    u = User(tenant_id=tenant.id, username="admin2", password_hash="x", full_name="审核员2", is_active=True)
    session.add(u)
    session.flush()
    session.execute(user_roles.insert().values(user_id=u.id, role_id=admin_role.id))
    session.flush()
    return u


@pytest.fixture()
def boss(tenant, admin_role, session):
    """超级管理员（IM 卡片通道权限判断用）。"""
    u = User(
        tenant_id=tenant.id, username="boss", password_hash="x", full_name="王老板",
        is_active=True, is_superuser=True,
    )
    session.add(u)
    session.flush()
    session.execute(user_roles.insert().values(user_id=u.id, role_id=admin_role.id))
    session.flush()
    return u


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(reports_module.router, prefix="/admin/reports")
    app.include_router(units_module.router, prefix="/admin/production")
    app.include_router(temp_module.router, prefix="/admin/production")
    holder = {"user": test_user}
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: holder["user"]
    app.dependency_overrides[get_current_permissions] = lambda: ["report.audit"]
    client = TestClient(app)
    client.holder = holder  # 测试中切换当前登录用户
    return client


def _mk_task(session, tenant, customer, product, sku, process, planned=100, code="T-001"):
    order = Order(tenant_id=tenant.id, customer_id=customer.id, code=f"SO-{code}", status="confirmed")
    session.add(order)
    session.flush()
    item = OrderItem(
        tenant_id=tenant.id, order_id=order.id, line_no=1, sku_id=sku.id, qty=planned,
        unit_price=Decimal("10"), subtotal=Decimal("1000"),
    )
    session.add(item)
    session.flush()
    wo = WorkOrder(
        tenant_id=tenant.id, order_id=order.id, order_item_id=item.id,
        product_id=product.id, sku_id=sku.id, qty=planned, status="open",
    )
    session.add(wo)
    session.flush()
    task = Task(
        tenant_id=tenant.id, work_order_id=wo.id, process_id=process.id, seq=1,
        task_code=code, planned_qty=planned, status="pending",
    )
    session.add(task)
    session.flush()
    return task


def _mk_report(session, tenant, task, report_user_id, qty=10):
    r = Report(
        tenant_id=tenant.id, task_id=task.id, report_user_id=report_user_id,
        good_qty=qty, bad_qty=0, status="submitted",
    )
    session.add(r)
    session.flush()
    return r


def _mk_unit(session, tenant, task, user_id, assigned_qty=10, unit_seq=1):
    a = TaskAssignment(tenant_id=tenant.id, task_id=task.id, user_id=user_id, assigned_qty=assigned_qty)
    session.add(a)
    session.flush()
    u = ReportUnit(
        tenant_id=tenant.id, task_assignment_id=a.id, task_id=task.id, user_id=user_id,
        unit_seq=unit_seq, result_type="good", status="submitted",
    )
    session.add(u)
    session.flush()
    return u


def _audits(session, report_id):
    return session.scalars(
        select(ReportAudit).where(ReportAudit.report_id == report_id).order_by(ReportAudit.id)
    ).all()


# ---------- admin 报工端点 ----------

def test_leader_approve_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user):
    """自报自审：初审拦截，状态不变且无审核流水。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, test_user.id, qty=10)

    r = api.post(f"/admin/reports/{report.id}/leader-approve")
    assert r.status_code == 400
    assert "职责分离" in r.json()["detail"]

    session.refresh(report)
    assert report.status == "submitted"
    assert _audits(session, report.id) == []


def test_qc_approve_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user, worker):
    """报工人本人终审被拦截（初审由他人完成）。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, worker.id, qty=10)

    r1 = api.post(f"/admin/reports/{report.id}/leader-approve")
    assert r1.status_code == 200, r1.text

    # 切换为报工人本人调用（权限 override 仍为 report.audit，模拟其恰好有审核权）
    api.holder["user"] = worker
    r2 = api.post(f"/admin/reports/{report.id}/qc-approve")
    assert r2.status_code == 400
    assert "本人提交" in r2.json()["detail"]
    session.refresh(report)
    assert report.status == "leader_approved"


def test_qc_approve_same_person_as_leader_rejected(api, session, tenant, customer, product, sku, process, process_price, test_user, auditor2, worker):
    """初审/终审不得同一人；换人后终审通过，两级留痕完整。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, worker.id, qty=10)

    r1 = api.post(f"/admin/reports/{report.id}/leader-approve")
    assert r1.status_code == 200, r1.text

    r2 = api.post(f"/admin/reports/{report.id}/qc-approve")
    assert r2.status_code == 400
    assert "同一人" in r2.json()["detail"]

    # 换第二位审核人终审 → 通过
    api.holder["user"] = auditor2
    r3 = api.post(f"/admin/reports/{report.id}/qc-approve")
    assert r3.status_code == 200, r3.text
    assert r3.json()["data"]["status"] == "qc_approved"

    audits = _audits(session, report.id)
    assert [(a.audit_level, a.auditor_id) for a in audits] == [("leader", test_user.id), ("qc", auditor2.id)]


def test_reject_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user, auditor2):
    """驳回同属审核动作：自审拦截；他人驳回通过。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, test_user.id, qty=10)

    r = api.post(f"/admin/reports/{report.id}/reject")
    assert r.status_code == 400
    assert "职责分离" in r.json()["detail"]

    api.holder["user"] = auditor2
    r2 = api.post(f"/admin/reports/{report.id}/reject")
    assert r2.status_code == 200, r2.text
    session.refresh(report)
    assert report.status == "rejected"


# ---------- admin 件次端点 ----------

def test_unit_approve_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user):
    """件次自审拦截。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    unit = _mk_unit(session, tenant, task, test_user.id)

    r = api.post(f"/admin/production/report-units/{unit.id}/approve", json={})
    assert r.status_code == 400
    assert "职责分离" in r.json()["detail"]
    session.refresh(unit)
    assert unit.status == "submitted"


def test_unit_same_person_two_levels_rejected(api, session, tenant, customer, product, sku, process, test_user, worker):
    """件次同一人不得审两级：初审通过后同一人再终审被拦。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    unit = _mk_unit(session, tenant, task, worker.id)

    r1 = api.post(f"/admin/production/report-units/{unit.id}/approve", json={})
    assert r1.status_code == 200, r1.text
    assert r1.json()["data"]["status"] == "leader_approved"

    r2 = api.post(
        f"/admin/production/report-units/{unit.id}/approve",
        json={"qc_attachment_ids": "att1"},
    )
    assert r2.status_code == 400
    assert "职责分离" in r2.json()["detail"]
    session.refresh(unit)
    assert unit.status == "leader_approved"


def test_unit_reject_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user):
    """件次驳回自审拦截。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    unit = _mk_unit(session, tenant, task, test_user.id)

    r = api.post(f"/admin/production/report-units/{unit.id}/reject")
    assert r.status_code == 400
    assert "职责分离" in r.json()["detail"]


# ---------- 临时报工绑定（绑定即终审） ----------

def test_temp_bind_self_audit_rejected(api, session, tenant, customer, product, sku, process, test_user):
    """临时报工绑定即终审：不得绑定本人提交的临时报工。"""
    task = _mk_task(session, tenant, customer, product, sku, process)
    temp = TempReport(tenant_id=tenant.id, user_id=test_user.id, good_qty=10, bad_qty=0, status="pending")
    session.add(temp)
    session.flush()

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 10})
    assert r.status_code == 400
    assert "职责分离" in r.json()["detail"]


# ---------- IM / 企微卡片通道（服务层） ----------

def test_im_card_self_audit_raises(session, tenant, customer, product, sku, process, boss):
    """飞书/钉钉卡片：超级管理员自己报工后再自审被拦。"""
    from app.services.report_audit_actions import ReportAuditError, leader_approve_report, reject_report

    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, boss.id, qty=10)

    with pytest.raises(ReportAuditError, match="职责分离"):
        leader_approve_report(session, tenant_id=tenant.id, report_id=report.id, auditor=boss)
    with pytest.raises(ReportAuditError, match="职责分离"):
        reject_report(session, tenant_id=tenant.id, report_id=report.id, auditor=boss)


def test_wecom_card_self_audit_raises(session, tenant, customer, product, sku, process, boss):
    """企微卡片：超级管理员自己报工后再自审被拦。"""
    from app.services.wecom.audit_actions import WecomAuditError, leader_approve_report as wecom_approve

    task = _mk_task(session, tenant, customer, product, sku, process)
    report = _mk_report(session, tenant, task, boss.id, qty=10)

    with pytest.raises(WecomAuditError, match="职责分离"):
        wecom_approve(session, tenant_id=tenant.id, report_id=report.id, auditor=boss)
