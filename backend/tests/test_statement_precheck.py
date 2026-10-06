"""对账金额口径统一（P2-24）回归测试

背景：
- 订单确认侧 _fill_order_amount 容错（缺工价记 0 不报错），而对账侧
  calc_order_statement_amount 缺工价直接 raise → 订单能确认、对账必失败；
- 且 POST /finance 逐单遇错即抛，多单缺价只能"修一单、报一单"式试错，
  无默认工艺路线时还会给出不带订单号的裸报错。

修复：
- crud/finance.scan_order_statement 统一扫描：返回 (金额, 问题列表)，
  不抛异常，问题含 no_items / sku_missing / no_route / missing_price；
- POST /finance 全量收集 blocked 后一次性 400 提示（附修复指引）；
- 新增 GET /statements/precheck 预检：逐单返回 ok/reason/issues，不写库、不阻断。

覆盖：
- 预检：正常金额 / 缺工价 issue / 无路线 issue（不 500）/ 已入账 / 不存在单 /
  客户不匹配 / 不写库
- 创建：两单缺价聚合报错同时列出 / 补工价后成功
- 兼容：calc_order_statement_amount 保持 raise 行为（缺工价、无明细）
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.admin.finance import router as finance_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.finance import calc_order_statement_amount
from app.models.customer import Customer
from app.models.finance import Statement, StatementItem
from app.models.order import Order, OrderItem
from app.models.process_price import ProcessPrice


def _mk_order(session, tenant_id, customer_id, sku_id=None, code="SO001", qty=10, with_item=True):
    o = Order(tenant_id=tenant_id, customer_id=customer_id, code=code, status="confirmed")
    session.add(o)
    session.flush()
    if with_item:
        session.add(OrderItem(tenant_id=tenant_id, order_id=o.id, line_no=1, sku_id=sku_id, qty=qty))
        session.flush()
    return o


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(finance_module.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["finance.manage"]
    return TestClient(app)


def _precheck(api, customer_id, order_ids):
    r = api.get("/finance/statements/precheck", params={"customer_id": customer_id, "order_ids": order_ids})
    assert r.status_code == 200, r.text
    return r.json()["data"]


# ---------------- 预检 ----------------

def test_precheck_ok_amount(api, session, tenant, customer, sku, process_route, process_price):
    """正常订单：all_ok，金额=数量×工价（10 × 1.50）。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-1")
    data = _precheck(api, customer.id, str(order.id))
    assert data["all_ok"] is True
    assert data["ok_count"] == 1 and data["blocked_count"] == 0
    it = data["items"][0]
    assert it["ok"] is True and it["reason"] is None
    assert it["amount"] == 15.0
    assert it["issues"] == []


def test_precheck_missing_price_issue(api, session, tenant, customer, sku, process_route, process):
    """有路线但缺工价：reason=has_issues，issue 含 missing_process_ids。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-2")
    data = _precheck(api, customer.id, str(order.id))
    assert data["all_ok"] is False and data["blocked_count"] == 1
    it = data["items"][0]
    assert it["ok"] is False and it["reason"] == "has_issues" and it["amount"] is None
    issue = it["issues"][0]
    assert issue["type"] == "missing_price"
    assert issue["missing_process_ids"] == [process.id]
    assert f"process_id={process.id}" in issue["message"]


def test_precheck_no_route_issue(api, session, tenant, customer, sku):
    """无默认工艺路线：转为 no_route issue（不 500），message 带订单与型号。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-3")
    data = _precheck(api, customer.id, str(order.id))
    it = data["items"][0]
    assert it["reason"] == "has_issues"
    issue = it["issues"][0]
    assert issue["type"] == "no_route"
    assert "SO-PRE-3" in issue["message"] and "工艺路线" in issue["message"]


def test_precheck_already_stated(api, session, tenant, customer, sku, process_route, process_price):
    """已入账订单：reason=already_stated，提示已在对账单号。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-4")
    r = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(order.id)})
    assert r.status_code == 200, r.text
    code = r.json()["data"]["code"]

    data = _precheck(api, customer.id, str(order.id))
    it = data["items"][0]
    assert it["ok"] is False and it["reason"] == "already_stated"
    assert code in it["issues"][0]["message"]


def test_precheck_not_found_and_customer_mismatch(api, session, tenant, customer, sku, process_route, process_price):
    """不存在的订单 → not_found；他客户订单 → customer_mismatch。"""
    other = Customer(tenant_id=tenant.id, code="C002", name="他客户", is_active=True)
    session.add(other)
    session.flush()
    o_other = _mk_order(session, tenant.id, other.id, sku.id, code="SO-PRE-5B")

    data = _precheck(api, customer.id, f"999999,{o_other.id}")
    assert data["ok_count"] == 0 and data["blocked_count"] == 2
    by_id = {x["order_id"]: x for x in data["items"]}
    assert by_id[999999]["reason"] == "not_found"
    assert by_id[o_other.id]["reason"] == "customer_mismatch"
    assert by_id[o_other.id]["code"] == "SO-PRE-5B"


def test_precheck_does_not_write(api, session, tenant, customer, sku, process_route, process_price):
    """预检不写库：执行后无任何对账单/明细。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-6")
    _precheck(api, customer.id, str(order.id))
    assert session.scalar(select(func.count(Statement.id))) == 0
    assert session.scalar(select(func.count(StatementItem.id))) == 0


# ---------------- 创建（聚合报错） ----------------

def test_create_aggregates_all_blocked(api, session, tenant, customer, sku, process_route):
    """两个缺价订单：400 一次性列出两单问题（而非只报第一单），附修复指引。"""
    o1 = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-7A")
    o2 = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-7B")
    r = api.post("/finance", params={"customer_id": customer.id, "order_ids": f"{o1.id},{o2.id}"})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "SO-PRE-7A" in detail and "SO-PRE-7B" in detail
    assert "维护型号工价" in detail
    # 拒绝时不落任何对账单
    assert session.scalar(select(func.count(Statement.id))) == 0


def test_create_ok_after_price_fixed(api, session, tenant, customer, sku, process_route, process):
    """先缺价 400，补录 ProcessPrice 后成功且金额正确。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-8")
    r1 = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(order.id)})
    assert r1.status_code == 400 and "SO-PRE-8" in r1.json()["detail"]

    session.add(ProcessPrice(
        tenant_id=tenant.id, sku_id=sku.id, process_id=process.id,
        unit_price="1.50", is_active=True,
    ))
    session.flush()

    r2 = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(order.id)})
    assert r2.status_code == 200, r2.text
    assert r2.json()["data"]["total_amount"] == 15.0


# ---------------- 兼容：calc 保持 raise ----------------

def test_calc_keeps_raise_on_missing_price(session, tenant, customer, sku, process_route):
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-PRE-9A")
    with pytest.raises(ValueError, match="缺少工序工价"):
        calc_order_statement_amount(session, tenant.id, order)


def test_calc_keeps_raise_on_no_items(session, tenant, customer):
    order = _mk_order(session, tenant.id, customer.id, code="SO-PRE-9B", with_item=False)
    with pytest.raises(ValueError, match="无明细行"):
        calc_order_statement_amount(session, tenant.id, order)
