"""外协结算落账（P1-14）回归测试

背景：settle 只改状态，不生成任何应付/ledger（审计 2.6）：
`unit_price × received_qty` 不落账 → 委外成本不进财务口径。

修复：
- settle 按「单价 × 实收数」写 `FinanceLedger(out/subcontract, party=supplier,
  statement_type=subcontract_order, biz_date=结算日)`；
- 幂等：同一单据已存在同类流水不重复记账（防状态回退重结算）；金额 0 不记账；
- `profit_api` 成本并入外协：新增 `subcontract_cost`，`cost = 采购 + 人工 + 外协`。

覆盖：
- 结算落账：金额（多项求和）/方向/类别/往来单位/单据锚点/日期
- 重复结算 400（状态守卫，不重复记账）；状态回退重结算幂等
- 零金额不记账；未收货状态不可结算（既有护栏回归）
- 利润口径：subcontract_cost 计入成本与毛利
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.finance import router as finance_router_module
from app.api.admin.subcontract import router as subcontract_router_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.finance_ledger import create_ledger
from app.models.finance_ledger import FinanceLedger
from app.models.material import Supplier
from app.models.sku import Sku
from app.models.subcontract import SubcontractOrder, SubcontractOrderItem


@pytest.fixture()
def supplier(tenant, session):
    s = Supplier(tenant_id=tenant.id, code="SUP001", name="外协供应商")
    session.add(s)
    session.flush()
    return s


def _mk_sc(session, tenant, supplier, items, code="SC-001", status="received"):
    """items: list of (sku_id, qty, unit_price)"""
    sc = SubcontractOrder(tenant_id=tenant.id, supplier_id=supplier.id, code=code, status=status)
    session.add(sc)
    session.flush()
    for sku_id, qty, unit_price in items:
        session.add(SubcontractOrderItem(
            tenant_id=tenant.id, order_id=sc.id, sku_id=sku_id,
            qty=qty, unit_price=unit_price, sent_qty=qty, received_qty=qty,
        ))
    session.flush()
    return sc


@pytest.fixture()
def sub_api(session, test_user):
    app = FastAPI()
    app.include_router(subcontract_router_module.router, prefix="/admin/subcontract")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["subcontract.manage"]
    return TestClient(app)


def _ledgers(session, statement_type, statement_id):
    return session.scalars(
        select(FinanceLedger).where(
            FinanceLedger.statement_type == statement_type,
            FinanceLedger.statement_id == statement_id,
        ).order_by(FinanceLedger.id)
    ).all()


def test_settle_writes_subcontract_ledger(sub_api, session, tenant, supplier, product, sku, test_user):
    """结算落账：多项求和金额 + 归属 + 单据锚点。"""
    sku2 = Sku(tenant_id=tenant.id, product_id=product.id, code="SKU002", name="型号B", is_active=True)
    session.add(sku2)
    session.flush()
    sc = _mk_sc(session, tenant, supplier, [
        (sku.id, 10, Decimal("2.50")),
        (sku2.id, 5, Decimal("3")),
    ])

    r = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "settled"

    leds = _ledgers(session, "subcontract_order", sc.id)
    assert len(leds) == 1
    led = leds[0]
    assert led.direction == "out"
    assert led.category == "subcontract"
    assert led.party_type == "supplier"
    assert led.party_id == supplier.id
    assert float(led.amount) == 40.0  # 2.5×10 + 3×5
    assert led.biz_date == date.today()
    assert "外协结算#SC-001" in led.remark
    assert led.created_by == test_user.id


def test_settle_repeat_rejected_no_double_ledger(sub_api, session, tenant, supplier, sku):
    """重复结算：状态守卫 400，不重复记账。"""
    sc = _mk_sc(session, tenant, supplier, [(sku.id, 10, Decimal("2"))], code="SC-002")

    r1 = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r1.status_code == 200, r1.text
    r2 = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r2.status_code == 400
    assert "仅已收货可结算" in r2.json()["detail"]
    assert len(_ledgers(session, "subcontract_order", sc.id)) == 1


def test_settle_status_rollback_no_double_ledger(sub_api, session, tenant, supplier, sku):
    """状态被异常回退后重结算：ledger 幂等兜底，不重复记账。"""
    sc = _mk_sc(session, tenant, supplier, [(sku.id, 10, Decimal("2"))], code="SC-003")
    assert sub_api.post(f"/admin/subcontract/{sc.id}/settle").status_code == 200

    sc.status = "received"  # 模拟状态回退
    session.flush()
    r = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r.status_code == 200, r.text
    assert len(_ledgers(session, "subcontract_order", sc.id)) == 1


def test_settle_zero_price_no_ledger(sub_api, session, tenant, supplier, sku):
    """全部无单价：金额 0 不记账，仍置 settled。"""
    sc = _mk_sc(session, tenant, supplier, [(sku.id, 10, None)], code="SC-004")

    r = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "settled"
    assert _ledgers(session, "subcontract_order", sc.id) == []


def test_settle_only_received_allowed(sub_api, session, tenant, supplier, sku):
    """未收货状态不可结算（既有护栏回归，且不落账）。"""
    sc = _mk_sc(session, tenant, supplier, [(sku.id, 10, Decimal("2"))], code="SC-005", status="sent")

    r = sub_api.post(f"/admin/subcontract/{sc.id}/settle")
    assert r.status_code == 400
    assert _ledgers(session, "subcontract_order", sc.id) == []


def test_profit_includes_subcontract_cost(session, tenant, test_user):
    """利润口径：out/subcontract 计入成本（subcontract_cost）。"""
    create_ledger(
        session,
        tenant_id=tenant.id,
        direction="out",
        category="subcontract",
        party_type="supplier",
        party_id=None,
        statement_type="subcontract_order",
        statement_id=1,
        amount=Decimal("100"),
        biz_date=date(2026, 10, 2),
        remark="外协结算",
        created_by=test_user.id,
    )

    app = FastAPI()
    app.include_router(finance_router_module.router, prefix="/admin/finance")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["finance.manage"]
    client = TestClient(app)

    r = client.get("/admin/finance/profit", params={"month": "2026-10"})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["subcontract_cost"] == 100.0
    assert d["cost"] == 100.0  # 采购 0 + 人工 0 + 外协 100
    assert d["gross_profit"] == -100.0
