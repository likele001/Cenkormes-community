"""留痕补口（P1-15）回归测试

背景：审计发现敏感操作缺结构化留痕（operation_logs）：
- 工资条重置（reset-confirm）：清空签收/拒签信息，仅发通知不落日志
- 手工记账（POST /finance/ledgers）：资金流水手工录入无日志
- 手工调库存（POST /warehouse/stocks/adjust）：库存调整无日志
- 订单驳回：只把原因追加进 remark 文本，无结构化留痕

修复：4 处均写 operation_logs（复用 write_op_log，含操作人/租户/对象/明细/路径）。

覆盖：
- 订单驳回：写 op log（module=order/action=reject），detail 含单号与原因；操作人/租户正确
- 订单驳回失败（状态不符）：400 且不留痕
- 手工记账：写 op log（module=finance/action=create_ledger），detail 含方向/金额；流水正常落库
- 手工记账参数不合法：400 且不留痕
- 工资条重置：写 op log（module=salary/action=reset_confirm），detail 含员工与月份
- 手工调库存：写 op log（module=warehouse/action=adjust_stock），detail 含变动数与余额
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.finance import router as finance_router_module
from app.api.admin.production import orders as orders_module
from app.api.admin.production import salary_reports as salary_reports_module
from app.api.admin.warehouse import router as warehouse_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.salary_slip import ensure_salary_slip
from app.models.finance_ledger import FinanceLedger
from app.models.operation_log import OperationLog
from app.models.order import Order
from app.models.user import User
from app.models.warehouse import Warehouse


@pytest.fixture()
def emp(session, tenant) -> User:
    u = User(tenant_id=tenant.id, username="emp1", password_hash="x", full_name="张三", is_active=True)
    session.add(u)
    session.flush()
    return u


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(orders_module.router, prefix="/admin/production/orders")
    app.include_router(finance_router_module.router, prefix="/admin/finance")
    app.include_router(salary_reports_module.router, prefix="/admin/production/reports")
    app.include_router(warehouse_module.router, prefix="/admin/warehouse")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: [
        "order.manage", "finance.manage", "salary.manage", "warehouse.manage",
    ]
    return TestClient(app)


def _logs(session, module: str, action: str, object_id: int | None = None) -> list[OperationLog]:
    stmt = select(OperationLog).where(OperationLog.module == module, OperationLog.action == action)
    if object_id is not None:
        stmt = stmt.where(OperationLog.object_id == object_id)
    return list(session.scalars(stmt).all())


# ── 订单驳回 ──

def test_order_reject_writes_op_log(api, session, tenant, test_user, customer):
    """订单驳回：写结构化留痕（操作人/租户/对象/原因/路径齐全）。"""
    order = Order(tenant_id=tenant.id, customer_id=customer.id, code="SO-1001", status="pending_confirm")
    session.add(order)
    session.flush()

    r = api.post(f"/admin/production/orders/{order.id}/reject", params={"reason": "价格有误"})
    assert r.status_code == 200, r.text
    session.refresh(order)
    assert order.status == "draft"
    assert "[驳回]" in (order.remark or "")  # 原有 remark 追加行为保留

    logs = _logs(session, "order", "reject", object_id=order.id)
    assert len(logs) == 1
    lg = logs[0]
    assert lg.tenant_id == tenant.id
    assert lg.user_id == test_user.id
    assert lg.username == test_user.username
    assert lg.object_type == "Order"
    assert "SO-1001" in (lg.detail or "")
    assert "价格有误" in (lg.detail or "")
    assert lg.method == "POST"
    assert lg.path == f"/admin/production/orders/{order.id}/reject"


def test_order_reject_invalid_state_no_log(api, session, tenant, customer):
    """驳回失败（非待审核状态）：400 且不留痕。"""
    order = Order(tenant_id=tenant.id, customer_id=customer.id, code="SO-1002", status="draft")
    session.add(order)
    session.flush()

    r = api.post(f"/admin/production/orders/{order.id}/reject", params={"reason": "x"})
    assert r.status_code == 400
    assert _logs(session, "order", "reject", object_id=order.id) == []


# ── 手工记账 ──

def test_manual_ledger_writes_op_log(api, session, tenant, test_user, customer):
    """手工记账：流水正常落库 + 写 op log（明细含方向/类别/金额）。"""
    r = api.post("/admin/finance/ledgers", json={
        "direction": "in",
        "category": "receipt",
        "party_type": "customer",
        "party_id": customer.id,
        "amount": "1234.50",
        "biz_date": "2026-10-05",
        "remark": "手工回款",
    })
    assert r.status_code == 200, r.text
    led_id = r.json()["data"]["id"]

    led = session.get(FinanceLedger, led_id)
    assert led is not None
    assert float(led.amount) == 1234.50

    logs = _logs(session, "finance", "create_ledger", object_id=led_id)
    assert len(logs) == 1
    lg = logs[0]
    assert lg.tenant_id == tenant.id
    assert lg.user_id == test_user.id
    assert lg.object_type == "FinanceLedger"
    assert "direction=in" in (lg.detail or "")
    assert "category=receipt" in (lg.detail or "")
    assert "1234.50" in (lg.detail or "")


def test_manual_ledger_invalid_no_log(api, session, tenant):
    """手工记账参数不合法（往来单位缺ID）：400 且不留痕。"""
    r = api.post("/admin/finance/ledgers", json={
        "direction": "in",
        "category": "receipt",
        "party_type": "customer",
        "amount": "10",
        "biz_date": "2026-10-05",
    })
    assert r.status_code == 400
    assert _logs(session, "finance", "create_ledger") == []


# ── 工资条重置 ──

def test_salary_reset_writes_op_log(api, session, tenant, test_user, emp):
    """工资条重置：清空拒签信息 + 写 op log（明细含员工/月份）。"""
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month="2026-09")
    slip.confirm_status = "rejected"
    slip.reject_reason = "金额有误"
    session.flush()

    r = api.post(f"/admin/production/reports/salary/slips/{slip.id}/reset-confirm")
    assert r.status_code == 200, r.text
    session.refresh(slip)
    assert slip.confirm_status == "pending"
    assert slip.reject_reason is None

    logs = _logs(session, "salary", "reset_confirm", object_id=slip.id)
    assert len(logs) == 1
    lg = logs[0]
    assert lg.tenant_id == tenant.id
    assert lg.user_id == test_user.id
    assert lg.object_type == "SalarySlip"
    assert f"user_id={emp.id}" in (lg.detail or "")
    assert "2026-09" in (lg.detail or "")


# ── 手工调库存（回归保护：已有实现） ──

def test_stock_adjust_writes_op_log(api, session, tenant, test_user, sku):
    """手工调库存：库存变动 + 写 op log（明细含变动数/余额）。"""
    wh = Warehouse(tenant_id=tenant.id, code="WH01", name="主仓")
    session.add(wh)
    session.flush()

    r = api.post("/admin/warehouse/stocks/adjust", params={
        "warehouse_id": wh.id,
        "sku_id": sku.id,
        "change_qty": 10,
        "remark": "盘盈",
    })
    assert r.status_code == 200, r.text
    assert r.json()["data"]["qty"] == 10

    logs = _logs(session, "warehouse", "adjust_stock")
    assert len(logs) == 1
    lg = logs[0]
    assert lg.tenant_id == tenant.id
    assert lg.user_id == test_user.id
    assert "change_qty=10" in (lg.detail or "")
    assert "balance=10" in (lg.detail or "")
