"""临时报工绑定补校验 + 留痕（P1-12）回归测试

背景：绑定端点将临时报工并入正式任务（审计 Part 1 #12）：
- 只校验临时报工自身剩余数量，未校验任务派工/计划上限，
  可借临时报工绕过派工额度（多绑/超绑）；
- "绑定即终审"（submitted → qc_approved）直接改状态，不写 ReportAudit，
  审核动作无留痕。

修复：
- 派工上限：员工在该任务有派工记录时，绑定后累计报工不得超派工数（400）；
- 计划上限：任务累计终审合格数 + 本次绑定不得超任务计划数（400，
  未派工员工绑定的兜底护栏）；
- 绑定成功写 ReportAudit（audit_level=qc / action=approve，
  reason 记录来源临时报工 id 与数量）。

覆盖：
- 正常绑定：报工 qc_approved + ReportAudit 字段 + 计件工资；部分绑定保留 pending
- 拆单绑定：30 + 20 = 派工上限，恰好通过并置 bound；bound 后再绑 400
- 派工上限：超 400 且无副作用，恰好到边界通过
- 计划上限：未派工员工超计划余量 400，余量内通过
- 既有护栏：超临时报工剩余数量 400
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.production import temp_reports as temp_reports_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.order import Order, OrderItem
from app.models.report import Report, ReportAudit
from app.models.salary import SalaryItem
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
def api(session, test_user):
    app = FastAPI()
    app.include_router(temp_reports_module.router, prefix="/admin/production")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["report.audit"]
    return TestClient(app)


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


def _assign(session, tenant, task, user_id, qty, by):
    a = TaskAssignment(tenant_id=tenant.id, task_id=task.id, user_id=user_id, assigned_qty=qty, assigned_by=by)
    session.add(a)
    session.flush()
    return a


def _mk_temp(session, tenant, user_id, total=50):
    t = TempReport(
        tenant_id=tenant.id, user_id=user_id, good_qty=total, bad_qty=0,
        remark="无单补记", status="pending",
    )
    session.add(t)
    session.flush()
    return t


def _mk_done_report(session, tenant, task, user_id, qty):
    r = Report(
        tenant_id=tenant.id, task_id=task.id, report_user_id=user_id,
        good_qty=qty, bad_qty=0, status="qc_approved",
    )
    session.add(r)
    session.flush()
    return r


def _audits(session, report_id):
    return session.scalars(
        select(ReportAudit).where(ReportAudit.report_id == report_id).order_by(ReportAudit.id)
    ).all()


def test_bind_ok_writes_audit_and_salary(api, session, tenant, customer, product, sku, process, process_price, test_user, worker):
    """正常绑定：写 ReportAudit 留痕 + 计件工资，部分绑定保留 pending。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    _assign(session, tenant, task, worker.id, 50, test_user.id)
    temp = _mk_temp(session, tenant, worker.id, total=50)

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 30})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["qty_bound"] == 30
    assert d["status"] == "pending"  # 部分绑定，剩余 20 仍可继续绑

    report = session.get(Report, d["report_id"])
    assert report.status == "qc_approved"
    assert report.good_qty == 30

    audits = _audits(session, report.id)
    assert len(audits) == 1
    a = audits[0]
    assert a.tenant_id == tenant.id
    assert a.auditor_id == test_user.id
    assert a.audit_level == "qc"
    assert a.action == "approve"
    assert f"临时报工 #{temp.id}" in a.reason
    assert "数量 30" in a.reason

    salary = session.scalars(select(SalaryItem).where(SalaryItem.report_id == report.id)).all()
    assert len(salary) == 1
    assert salary[0].user_id == worker.id
    assert float(salary[0].amount) == 45.0  # 30 × 1.50

    session.refresh(temp)
    assert temp.bound_task_id == task.id
    assert temp.bound_by == test_user.id
    assert temp.qty_bound == 30


def test_bind_split_then_complete(api, session, tenant, customer, product, sku, process, test_user, worker):
    """拆单绑定：30 + 20 = 50（恰为派工上限）→ bound；bound 后再绑 400。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    _assign(session, tenant, task, worker.id, 50, test_user.id)
    temp = _mk_temp(session, tenant, worker.id, total=50)

    r1 = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 30})
    assert r1.status_code == 200, r1.text

    r2 = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 20})
    assert r2.status_code == 200, r2.text
    assert r2.json()["data"]["status"] == "bound"

    session.refresh(temp)
    assert temp.qty_bound == 50

    # bound 状态不可再绑
    r3 = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 5})
    assert r3.status_code == 400
    assert "仅待关联" in r3.json()["detail"]

    # 两次绑定各写一条审核流水
    reports = session.scalars(
        select(Report).where(Report.task_id == task.id, Report.status == "qc_approved").order_by(Report.id)
    ).all()
    assert len(reports) == 2
    for rep in reports:
        assert len(_audits(session, rep.id)) == 1


def test_bind_over_assignment_limit_rejected(api, session, tenant, customer, product, sku, process, test_user, worker):
    """派工 20、已报 15 → 绑 10 被 400 且无副作用；绑 5 恰好通过。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    _assign(session, tenant, task, worker.id, 20, test_user.id)
    _mk_done_report(session, tenant, task, worker.id, qty=15)
    temp = _mk_temp(session, tenant, worker.id, total=30)

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 10})
    assert r.status_code == 400
    assert "派工上限" in r.json()["detail"]
    assert "5" in r.json()["detail"]  # 最多还可绑 5 件

    # 无副作用：未生成新报工
    reports = session.scalars(
        select(Report).where(Report.task_id == task.id, Report.status == "qc_approved")
    ).all()
    assert len(reports) == 1

    # 恰好到边界可通过
    r2 = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 5})
    assert r2.status_code == 200, r2.text


def test_bind_over_task_plan_rejected(api, session, tenant, customer, product, sku, process, test_user, worker):
    """未派工员工绑定受任务计划上限约束：计划 100、已终审 90 → 绑 15 → 400。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    _mk_done_report(session, tenant, task, worker.id, qty=90)
    temp = _mk_temp(session, tenant, worker.id, total=15)

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 15})
    assert r.status_code == 400
    assert "计划上限" in r.json()["detail"]

    # 余量内（10 件）可通过
    r2 = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 10})
    assert r2.status_code == 200, r2.text


def test_bind_unassigned_employee_within_plan_ok(api, session, tenant, customer, product, sku, process, test_user, worker):
    """旧行为保留：未派工员工在计划余量内的绑定仍可成功，且写留痕。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    temp = _mk_temp(session, tenant, worker.id, total=20)

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 20})
    assert r.status_code == 200, r.text
    report_id = r.json()["data"]["report_id"]
    assert len(_audits(session, report_id)) == 1


def test_bind_over_temp_remaining_rejected(api, session, tenant, customer, product, sku, process, test_user, worker):
    """既有护栏回归：绑定不得超临时报工剩余数量。"""
    task = _mk_task(session, tenant, customer, product, sku, process, planned=100)
    temp = _mk_temp(session, tenant, worker.id, total=20)

    r = api.post(f"/admin/production/temp-reports/{temp.id}/bind", json={"task_id": task.id, "qty_bound": 25})
    assert r.status_code == 400
    assert "剩余可绑" in r.json()["detail"]
