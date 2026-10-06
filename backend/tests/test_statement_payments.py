"""核销能力（P1-10）回归测试

背景：对账 mark-paid 一次性全额置 paid + 一条幂等 ledger；无逐笔核销、
无部分收款、无 due_date/账龄（审计 Part 1 #5）。

修复：
- 新表 statement_payments（statement_type=customer/supplier）逐笔核销
- Statement / SupplierStatement 增加 due_date；状态机 draft → confirmed → partial → paid
- 收款/付款端点：支持部分核销，超额 400；每次核销写一条 FinanceLedger
- mark-paid 改造为差额核销（幂等 + 自愈补历史缺登记）
- 列表/详情输出已核销/未核销/账龄天数与分桶

覆盖：
- aging_info 分桶 0-30/31-60/61-90/90+ 与已结清清空
- 销售侧：部分收款 → partial；补收 → paid；再收 400；超额 400；非法日期 400；draft 400
- 销售侧汇总：GET payments 返回记录/已收/未收/账龄
- mark-paid：无核销时全额记账；部分后仅补差额且幂等；已 paid 无核销记录时自愈补登记
- 供应商侧：逐笔付款写 out/payment 流水；超额 400；mark-paid 差额；自愈补 ledger+核销
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.finance import router as finance_router_module
from app.api.admin.purchase import statements as purchase_statements_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud import statement_payment as sp
from app.crud.finance import create_statement, update_statement_status
from app.models.finance_ledger import FinanceLedger
from app.models.material import Supplier
from app.models.order import Order
from app.models.statement_payment import StatementPayment
from app.models.supplier_statement import SupplierStatement


DUE = date(2026, 9, 1)


def _mk_stmt(session, tenant_id, customer_id, code="ST-001", status="confirmed", amount="1000", due_date=DUE):
    """客户对账单（含一笔订单明细），按需置状态。"""
    order = Order(tenant_id=tenant_id, customer_id=customer_id, code=f"SO-{code}", status="confirmed")
    session.add(order)
    session.flush()
    stmt = create_statement(
        session,
        tenant_id=tenant_id,
        customer_id=customer_id,
        code=code,
        order_amounts=[(order.id, Decimal(amount))],
        due_date=due_date,
    )
    if status != "draft":
        update_statement_status(session, stmt, status)
    session.flush()
    return stmt


def _mk_sup_stmt(session, tenant_id, code="PS-001", status="confirmed", amount="500", due_date=DUE):
    """供应商对账单（直接 ORM 构造，不依赖入库流水统计）。"""
    sup = Supplier(tenant_id=tenant_id, code=f"S-{code}", name="测试供应商", is_active=True)
    session.add(sup)
    session.flush()
    stmt = SupplierStatement(
        tenant_id=tenant_id,
        supplier_id=sup.id,
        code=code,
        period_from=date(2026, 9, 1),
        period_to=date(2026, 9, 30),
        due_date=due_date,
        amount=Decimal(amount),
        status=status,
    )
    session.add(stmt)
    session.flush()
    return stmt


def _payments(session, statement_type, statement_id):
    return session.scalars(
        select(StatementPayment)
        .where(
            StatementPayment.statement_type == statement_type,
            StatementPayment.statement_id == statement_id,
        )
        .order_by(StatementPayment.id)
    ).all()


def _ledgers(session, statement_type, statement_id, direction="in", category="receipt"):
    return session.scalars(
        select(FinanceLedger).where(
            FinanceLedger.statement_type == statement_type,
            FinanceLedger.statement_id == statement_id,
            FinanceLedger.direction == direction,
            FinanceLedger.category == category,
        )
    ).all()


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(finance_router_module.router, prefix="/admin/finance")
    app.include_router(purchase_statements_module.router, prefix="/admin/purchase/statements")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["finance.manage", "purchase.manage"]
    return TestClient(app)


# ---------- 账龄工具 ----------

def test_aging_info_buckets():
    assert sp.aging_info(date(2026, 1, 1), Decimal("1"), today=date(2026, 1, 31)) == (30, "0-30")
    assert sp.aging_info(date(2026, 1, 1), Decimal("1"), today=date(2026, 2, 15)) == (45, "31-60")
    assert sp.aging_info(date(2026, 1, 1), Decimal("1"), today=date(2026, 3, 15)) == (73, "61-90")
    assert sp.aging_info(date(2026, 1, 1), Decimal("1"), today=date(2026, 6, 1)) == (151, "90+")
    # 已结清 / 无基准日 → 清空
    assert sp.aging_info(date(2026, 1, 1), Decimal("0")) == (None, None)
    assert sp.aging_info(None, Decimal("100")) == (None, None)


# ---------- 销售侧逐笔收款 ----------

def test_customer_partial_then_settle(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, amount="1000")
    r = api.post(
        f"/admin/finance/{stmt.id}/payments",
        params={"amount": "300", "biz_date": "2026-09-20", "method": "bank", "remark": "首笔"},
    )
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["status"] == "partial"
    assert d["paid_amount"] == 300.0
    assert d["unpaid_amount"] == 700.0

    session.refresh(stmt)
    assert stmt.status == "partial"
    rows = _payments(session, sp.CUSTOMER, stmt.id)
    assert len(rows) == 1
    assert float(rows[0].amount) == 300.0
    assert rows[0].biz_date == date(2026, 9, 20)
    assert rows[0].method == "bank"
    leds = _ledgers(session, "statement", stmt.id)
    assert len(leds) == 1
    assert float(leds[0].amount) == 300.0
    assert leds[0].biz_date == date(2026, 9, 20)
    assert rows[0].ledger_id == leds[0].id

    # 补收结清
    r = api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "700"})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["status"] == "paid"
    assert d["unpaid_amount"] == 0.0
    assert len(_payments(session, sp.CUSTOMER, stmt.id)) == 2
    assert len(_ledgers(session, "statement", stmt.id)) == 2

    # 再收 → 已结清 400
    r = api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "1"})
    assert r.status_code == 400


def test_customer_overpay_and_invalid_date_rejected(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-002", amount="1000")
    r = api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "1500"})
    assert r.status_code == 400
    r = api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "100", "biz_date": "bad-date"})
    assert r.status_code == 400
    # 非法输入均不落库
    assert _payments(session, sp.CUSTOMER, stmt.id) == []
    assert _ledgers(session, "statement", stmt.id) == []


def test_customer_draft_rejected(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-003", status="draft")
    r = api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "100"})
    assert r.status_code == 400


def test_customer_payments_summary_with_aging(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-004", amount="1000")
    api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "250", "biz_date": "2026-09-20"})
    r = api.get(f"/admin/finance/{stmt.id}/payments")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert len(d["items"]) == 1
    assert d["total_amount"] == 1000.0
    assert d["paid_amount"] == 250.0
    assert d["unpaid_amount"] == 750.0
    assert d["due_date"] == "2026-09-01"
    expected_days = max(0, (date.today() - DUE).days)
    assert d["aging_days"] == expected_days
    assert d["aging_bucket"] is not None


# ---------- 销售侧 mark-paid 兼容与自愈 ----------

def test_customer_mark_paid_full_when_no_records(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-005", amount="1000")
    r = api.post(f"/admin/finance/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["status"] == "paid"
    assert d["paid_amount"] == 1000.0
    assert d["unpaid_amount"] == 0.0
    rows = _payments(session, sp.CUSTOMER, stmt.id)
    assert len(rows) == 1
    assert float(rows[0].amount) == 1000.0
    leds = _ledgers(session, "statement", stmt.id)
    assert len(leds) == 1

    # 幂等：重复 mark-paid 不重复记账
    r = api.post(f"/admin/finance/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    assert len(_payments(session, sp.CUSTOMER, stmt.id)) == 1
    assert len(_ledgers(session, "statement", stmt.id)) == 1


def test_customer_mark_paid_after_partial_gap_only(api, session, tenant, customer):
    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-006", amount="1000")
    api.post(f"/admin/finance/{stmt.id}/payments", params={"amount": "400"})
    r = api.post(f"/admin/finance/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    rows = _payments(session, sp.CUSTOMER, stmt.id)
    assert len(rows) == 2
    assert float(rows[1].amount) == 600.0  # 仅补差额
    leds = _ledgers(session, "statement", stmt.id)
    assert len(leds) == 2
    assert float(leds[1].amount) == 600.0
    assert stmt.status == "paid"


def test_customer_mark_paid_self_heal_missing_records(session, tenant, customer, test_user):
    """历史数据：status=paid + 已记 ledger + 无核销记录 → mark-paid 补核销、不重复记账。"""
    from app.crud import statement_payment as sp_mod

    stmt = _mk_stmt(session, tenant.id, customer.id, code="ST-007", amount="1000")
    update_statement_status(session, stmt, "paid")
    from app.crud.finance_ledger import create_ledger

    create_ledger(
        session,
        tenant_id=tenant.id,
        direction="in",
        category="receipt",
        party_type="customer",
        party_id=customer.id,
        statement_type="statement",
        statement_id=stmt.id,
        amount=Decimal("1000"),
        biz_date=DUE,
        remark="历史收款",
        created_by=test_user.id,
    )
    assert _payments(session, sp_mod.CUSTOMER, stmt.id) == []

    # 直接走 crud 层等价路径（API 层仅做状态判断）
    app = FastAPI()
    app.include_router(finance_router_module.router, prefix="/admin/finance")
    from app.core.deps import get_current_permissions, get_current_user, get_db

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["finance.manage"]
    client = TestClient(app)
    r = client.post(f"/admin/finance/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text

    rows = _payments(session, sp_mod.CUSTOMER, stmt.id)
    assert len(rows) == 1
    assert float(rows[0].amount) == 1000.0
    assert rows[0].remark == "历史收款补登记"
    leds = _ledgers(session, "statement", stmt.id)
    assert len(leds) == 1  # 不重复记账


# ---------- 供应商侧逐笔付款 ----------

def test_supplier_partial_payment(api, session, tenant):
    stmt = _mk_sup_stmt(session, tenant.id, amount="500")
    r = api.post(
        f"/admin/purchase/statements/{stmt.id}/payments",
        params={"amount": "200", "biz_date": "2026-09-25", "method": "bank", "remark": "首笔"},
    )
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["status"] == "partial"
    assert d["paid_amount"] == 200.0
    assert d["unpaid_amount"] == 300.0

    session.refresh(stmt)
    assert stmt.status == "partial"
    rows = _payments(session, sp.SUPPLIER, stmt.id)
    assert len(rows) == 1
    assert float(rows[0].amount) == 200.0
    leds = _ledgers(session, "supplier_statement", stmt.id, direction="out", category="payment")
    assert len(leds) == 1
    assert float(leds[0].amount) == 200.0
    assert leds[0].party_type == "supplier"

    # 汇总 + 账龄
    r = api.get(f"/admin/purchase/statements/{stmt.id}/payments")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["total_amount"] == 500.0
    assert d["paid_amount"] == 200.0
    assert d["unpaid_amount"] == 300.0
    assert d["due_date"] == "2026-09-01"
    assert d["aging_days"] == max(0, (date.today() - DUE).days)

    # 超额 400
    r = api.post(f"/admin/purchase/statements/{stmt.id}/payments", params={"amount": "301"})
    assert r.status_code == 400


def test_supplier_mark_paid_gap_only(api, session, tenant):
    stmt = _mk_sup_stmt(session, tenant.id, code="PS-002", amount="500")
    api.post(f"/admin/purchase/statements/{stmt.id}/payments", params={"amount": "200"})
    r = api.post(f"/admin/purchase/statements/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["status"] == "paid"
    assert d["paid_amount"] == 500.0
    assert d["unpaid_amount"] == 0.0

    rows = _payments(session, sp.SUPPLIER, stmt.id)
    assert len(rows) == 2
    assert float(rows[1].amount) == 300.0  # 仅补差额
    leds = _ledgers(session, "supplier_statement", stmt.id, direction="out", category="payment")
    assert len(leds) == 2

    # 幂等
    r = api.post(f"/admin/purchase/statements/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    assert len(_payments(session, sp.SUPPLIER, stmt.id)) == 2
    assert len(_ledgers(session, "supplier_statement", stmt.id, direction="out", category="payment")) == 2


def test_supplier_mark_paid_self_heal(api, session, tenant):
    """历史数据：status=paid 且无 ledger/核销 → mark-paid 补记账 + 补核销。"""
    stmt = _mk_sup_stmt(session, tenant.id, code="PS-003", amount="500", status="paid")
    assert _payments(session, sp.SUPPLIER, stmt.id) == []
    r = api.post(f"/admin/purchase/statements/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    rows = _payments(session, sp.SUPPLIER, stmt.id)
    assert len(rows) == 1
    assert float(rows[0].amount) == 500.0
    leds = _ledgers(session, "supplier_statement", stmt.id, direction="out", category="payment")
    assert len(leds) == 1
    assert float(leds[0].amount) == 500.0
