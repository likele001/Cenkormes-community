"""工资落账 + 利润口径（P1-9）回归测试

背景：SalarySlip 仅有签收状态（confirm_status），无发放状态/发放时间；
工资发放不写 FinanceLedger → 人工成本在现金流与毛利口径中缺位。

修复：
- SalarySlip 增加 pay_status/paid_at/paid_by/pay_method 四列
- 发放写 FinanceLedger(direction=out, category=labor, statement_type=salary_slip)
- profit_api 总成本 = 采购成本(payment/out) + 人工成本(labor/out)

覆盖：
- 发放端点：置 paid + 写 labor 流水（金额=实发、biz_date/pay_method 落库）
- 幂等：重复发放不重复记账、不覆盖发放时间
- 自愈：已置发放但缺流水（异常态）时补记
- 实发<=0：不写流水但仍置发放状态
- profit：labor 计入总成本，purchase/labor 拆分正确
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.admin.finance import router as finance_router_module
from app.api.admin.production import salary_reports
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.finance_ledger import create_ledger
from app.crud.salary_slip import ensure_salary_slip, pay_salary_slip
from app.models.finance_ledger import FinanceLedger
from app.models.notification import Notification
from app.models.user import User


@pytest.fixture()
def emp(session, tenant) -> User:
    u = User(tenant_id=tenant.id, username="emp1", password_hash="x", full_name="张三", is_active=True)
    session.add(u)
    session.flush()
    return u


def _mk_slip(session, tenant_id, user_id, month="2026-09", amount="500"):
    """造一张实发金额确定的工资条（直接设定金额，不依赖报工数据）。"""
    slip = ensure_salary_slip(session, tenant_id=tenant_id, user_id=user_id, month=month)
    slip.net_amount = Decimal(amount)
    session.flush()
    return slip


def _labor_ledgers(session, slip_id):
    return session.scalars(
        select(FinanceLedger).where(
            FinanceLedger.statement_type == "salary_slip",
            FinanceLedger.statement_id == slip_id,
            FinanceLedger.category == "labor",
            FinanceLedger.direction == "out",
        )
    ).all()


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(salary_reports.router, prefix="/admin/production/reports")
    app.include_router(finance_router_module.router, prefix="/admin/finance")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["salary.manage", "finance.manage"]
    return TestClient(app)


def test_pay_writes_labor_ledger(api, session, tenant, test_user, emp):
    """发放工资：置 paid + 写人工成本流水（金额/日期/方式/操作人）。"""
    slip = _mk_slip(session, tenant.id, emp.id, amount="500")
    r = api.post(
        f"/admin/production/reports/salary/slips/{slip.id}/pay",
        params={"pay_method": "bank", "biz_date": "2026-09-30"},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["pay_status"] == "paid"
    assert data["pay_method"] == "bank"

    session.refresh(slip)
    assert slip.pay_status == "paid"
    assert slip.paid_at is not None
    assert slip.paid_by == test_user.id
    assert slip.pay_method == "bank"

    leds = _labor_ledgers(session, slip.id)
    assert len(leds) == 1
    assert float(leds[0].amount) == 500.0
    assert leds[0].biz_date == date(2026, 9, 30)
    assert leds[0].created_by == test_user.id
    assert leds[0].statement_type == "salary_slip"
    assert "2026-09" in (leds[0].remark or "")

    cnt = session.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == emp.id, Notification.title == "工资已发放"
        )
    )
    assert cnt == 1


def test_pay_idempotent_no_double_ledger(api, session, tenant, emp):
    """重复发放：不重复记账、不覆盖发放时间与方式。"""
    slip = _mk_slip(session, tenant.id, emp.id, amount="800")
    r1 = api.post(f"/admin/production/reports/salary/slips/{slip.id}/pay")
    assert r1.status_code == 200, r1.text
    session.refresh(slip)
    first_paid_at = slip.paid_at
    first_method = slip.pay_method

    r2 = api.post(
        f"/admin/production/reports/salary/slips/{slip.id}/pay",
        params={"pay_method": "cash"},
    )
    assert r2.status_code == 200, r2.text
    session.refresh(slip)
    assert slip.paid_at == first_paid_at
    assert slip.pay_method == first_method  # 不覆盖首次发放方式
    assert len(_labor_ledgers(session, slip.id)) == 1


def test_pay_self_heal_missing_ledger(session, tenant, test_user, emp):
    """已置发放但缺流水（异常态）→ 再次发放时补记。"""
    slip = _mk_slip(session, tenant.id, emp.id, amount="300")
    slip.pay_status = "paid"
    slip.paid_at = datetime.now()
    session.flush()
    assert _labor_ledgers(session, slip.id) == []

    pay_salary_slip(session, tenant_id=tenant.id, slip_id=slip.id, paid_by=test_user.id)
    leds = _labor_ledgers(session, slip.id)
    assert len(leds) == 1
    assert float(leds[0].amount) == 300.0


def test_pay_non_positive_net_skips_ledger(session, tenant, test_user, emp):
    """实发<=0：置发放状态但不写流水（避免非法/无意义记账）。"""
    slip = _mk_slip(session, tenant.id, emp.id, amount="0")
    pay_salary_slip(session, tenant_id=tenant.id, slip_id=slip.id, paid_by=test_user.id)
    assert slip.pay_status == "paid"
    assert _labor_ledgers(session, slip.id) == []


def test_pay_invalid_biz_date_rejected(api, session, tenant, emp):
    slip = _mk_slip(session, tenant.id, emp.id)
    r = api.post(
        f"/admin/production/reports/salary/slips/{slip.id}/pay",
        params={"biz_date": "bad-date"},
    )
    assert r.status_code == 400


def test_pay_missing_slip_rejected(api, session, tenant):
    r = api.post("/admin/production/reports/salary/slips/999999/pay")
    assert r.status_code == 400


def test_profit_includes_labor_cost(api, session, tenant, test_user, emp, customer):
    """利润 = 收入 -（采购 + 人工），拆分字段正确。"""
    slip = _mk_slip(session, tenant.id, emp.id, amount="200")
    create_ledger(
        session,
        tenant_id=tenant.id,
        direction="in",
        category="receipt",
        party_type="customer",
        party_id=customer.id,
        statement_type=None,
        statement_id=None,
        amount=Decimal("1000"),
        biz_date=date(2026, 9, 10),
        remark="回款",
        created_by=test_user.id,
    )
    create_ledger(
        session,
        tenant_id=tenant.id,
        direction="out",
        category="payment",
        party_type="supplier",
        party_id=None,
        statement_type=None,
        statement_id=None,
        amount=Decimal("300"),
        biz_date=date(2026, 9, 11),
        remark="付款",
        created_by=test_user.id,
    )
    r = api.post(
        f"/admin/production/reports/salary/slips/{slip.id}/pay",
        params={"biz_date": "2026-09-12"},
    )
    assert r.status_code == 200, r.text

    r = api.get("/admin/finance/profit", params={"month": "2026-09"})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["revenue"] == 1000
    assert d["purchase_cost"] == 300
    assert d["labor_cost"] == 200
    assert d["cost"] == 500
    assert d["gross_profit"] == 500
    assert abs(d["gross_margin"] - 0.5) < 1e-9
