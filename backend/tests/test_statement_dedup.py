"""对账重复计费护栏（P0-6）回归测试

背景：
1. 销售侧对账单：同一订单可被重复选中入账，造成重复计费；
2. 供应商侧对账单：期间重叠时重复生成，同一入库流水被两次统计。

修复：
- 销售侧 POST /finance：生成前用 find_stated_order_ids 校验订单是否已进入
  任意对账单（任意状态）→ 400 拒绝，并提示已入账单号；
- 供应商侧 create_supplier_statement：新增流水级冲突检测
  （_find_duplicate_stockins）——同一入库流水同时落入本次期间与既有
  对账单期间、且该流水在既有对账单生成时已存在 → ValueError 拒绝。

覆盖：
- 销售侧：首次成功 / 同单重复 400 / 未入账新单不受影响 / 同请求重复单号去重
- 供应商侧：首次成功 / 同期间重复拒绝 / 跨期增量正常 / 全量单后续期间拒绝 / 空期间报错
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.admin.finance import router as finance_module
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.supplier_statement import create_supplier_statement
from app.models.finance import StatementItem
from app.models.material import Material, Supplier
from app.models.order import Order, OrderItem
from app.models.purchase import PurchaseOrder, PurchaseOrderItem
from app.models.warehouse import StockLog, Warehouse


# ---------------- 时间辅助（动态月份，避免依赖真实日期） ----------------

def _month_bounds(d: date) -> tuple[date, date]:
    """d 所在月的 (首日, 末日)。"""
    first = d.replace(day=1)
    next_first = (first + timedelta(days=32)).replace(day=1)
    return first, next_first - timedelta(days=1)


def _last_month() -> tuple[date, date]:
    """上个月 (首日, 末日)。"""
    return _month_bounds(date.today().replace(day=1) - timedelta(days=1))


def _prev2_month() -> tuple[date, date]:
    """上上个月 (首日, 末日)。"""
    return _month_bounds(_last_month()[0] - timedelta(days=1))


def _at(d: date) -> datetime:
    """该日 10:00 —— 恒早于对账单创建时间（now 所在月 ≥ 次月 1 日）。"""
    return datetime.combine(d, time(10, 0))


# ---------------- 公共造数 ----------------

def _mk_order(session, tenant_id, customer_id, sku_id, code="SO001", qty=10, line_no=1):
    o = Order(tenant_id=tenant_id, customer_id=customer_id, code=code, status="confirmed")
    session.add(o)
    session.flush()
    session.add(OrderItem(tenant_id=tenant_id, order_id=o.id, line_no=line_no, sku_id=sku_id, qty=qty))
    session.flush()
    return o


def _mk_supplier(session, tenant_id, code="SUP01"):
    s = Supplier(tenant_id=tenant_id, code=code, name="测试供应商")
    session.add(s)
    session.flush()
    return s


def _mk_material(session, tenant_id, sku_id, supplier_id, code="M001"):
    m = Material(tenant_id=tenant_id, code=code, name="测试物料", sku_id=sku_id, supplier_id=supplier_id)
    session.add(m)
    session.flush()
    return m


def _mk_po(session, tenant_id, supplier_id, code="PO001"):
    po = PurchaseOrder(tenant_id=tenant_id, supplier_id=supplier_id, code=code, status="confirmed")
    session.add(po)
    session.flush()
    return po


def _mk_po_item(session, tenant_id, order_id, material_id, unit_price="15"):
    it = PurchaseOrderItem(
        tenant_id=tenant_id, order_id=order_id, material_id=material_id,
        qty=100, unit_price=Decimal(unit_price),
    )
    session.add(it)
    session.flush()
    return it


def _mk_warehouse(session, tenant_id, code="WH01"):
    w = Warehouse(tenant_id=tenant_id, code=code, name="原料仓")
    session.add(w)
    session.flush()
    return w


def _mk_stockin(session, tenant_id, warehouse_id, sku_id, po_id, qty, created_at):
    """采购入库流水（显式 created_at 控制时序）。"""
    log = StockLog(
        tenant_id=tenant_id, warehouse_id=warehouse_id, sku_id=sku_id,
        change_qty=qty, balance_qty=qty, biz_type="purchase_in", biz_id=po_id,
        remark="采购入库", created_at=created_at,
    )
    session.add(log)
    session.flush()
    return log


@pytest.fixture()
def sup_env(session, tenant, sku):
    """供应商侧最小环境：供应商 + 物料(sku 绑定) + 采购单(单价15) + 仓库。"""
    supplier = _mk_supplier(session, tenant.id)
    material = _mk_material(session, tenant.id, sku.id, supplier.id)
    po = _mk_po(session, tenant.id, supplier.id)
    _mk_po_item(session, tenant.id, po.id, material.id, unit_price="15")
    wh = _mk_warehouse(session, tenant.id)
    return {"tenant_id": tenant.id, "supplier_id": supplier.id, "po_id": po.id, "warehouse_id": wh.id, "sku_id": sku.id}


# ---------------- 销售侧（TestClient） ----------------

@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(finance_module.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["finance.manage"]
    return TestClient(app)


def test_sales_first_statement_ok(api, session, tenant, customer, sku, process_route, process_price):
    """首次对账成功，金额=数量×工价；同请求重复单号仅计一次明细。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-DED-1")
    r = api.post("/finance", params={"customer_id": customer.id, "order_ids": f"{order.id},{order.id}"})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["total_amount"] == 15.0  # 10 × 1.50
    n = session.scalar(select(func.count(StatementItem.id)).where(StatementItem.order_id == order.id))
    assert n == 1  # 重复单号已去重


def test_sales_duplicate_order_rejected(api, session, tenant, customer, sku, process_route, process_price):
    """同一订单再次对账 → 400，且提示已入账单号（防重复计费核心）。"""
    order = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-DED-2")
    r1 = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(order.id)})
    assert r1.status_code == 200, r1.text
    code = r1.json()["data"]["code"]

    r2 = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(order.id)})
    assert r2.status_code == 400
    detail = r2.json()["detail"]
    assert f"订单 {order.id}" in detail and code in detail


def test_sales_new_order_unaffected(api, session, tenant, customer, sku, process_route, process_price):
    """已入账订单被拦截，但未入账新订单正常生成。"""
    o1 = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-DED-3A")
    o2 = _mk_order(session, tenant.id, customer.id, sku.id, code="SO-DED-3B", line_no=1)
    assert api.post("/finance", params={"customer_id": customer.id, "order_ids": str(o1.id)}).status_code == 200
    r = api.post("/finance", params={"customer_id": customer.id, "order_ids": str(o2.id)})
    assert r.status_code == 200, r.text


# ---------------- 供应商侧（直接调 crud） ----------------

def test_sup_first_statement_ok(session, sup_env):
    """首次对账成功：金额=入库数量×单价。"""
    pf, pt = _prev2_month()
    _mk_stockin(session, sup_env["tenant_id"], sup_env["warehouse_id"], sup_env["sku_id"],
                sup_env["po_id"], qty=10, created_at=_at(pt))
    stmt = create_supplier_statement(
        session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
        code=None, period_from=pf, period_to=pt,
    )
    assert stmt.amount == Decimal("150")  # 10 × 15
    assert len(stmt.items) == 1 and stmt.items[0].received_qty == 10


def test_sup_same_period_duplicate_rejected(session, sup_env):
    """同一期间重复生成 → 拒绝（同一入库流水二次统计）。"""
    pf, pt = _prev2_month()
    _mk_stockin(session, sup_env["tenant_id"], sup_env["warehouse_id"], sup_env["sku_id"],
                sup_env["po_id"], qty=10, created_at=_at(pt))
    create_supplier_statement(
        session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
        code=None, period_from=pf, period_to=pt,
    )
    with pytest.raises(ValueError, match="已在其他对账单"):
        create_supplier_statement(
            session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
            code=None, period_from=pf, period_to=pt,
        )


def test_sup_incremental_next_period_ok(session, sup_env):
    """跨期增量对账正常：新期间只统计新流水，不误伤旧期间。"""
    p2f, p2t = _prev2_month()
    p1f, p1t = _last_month()
    _mk_stockin(session, sup_env["tenant_id"], sup_env["warehouse_id"], sup_env["sku_id"],
                sup_env["po_id"], qty=10, created_at=_at(p2t))
    create_supplier_statement(
        session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
        code=None, period_from=p2f, period_to=p2t,
    )
    # 上月新增一批入库
    _mk_stockin(session, sup_env["tenant_id"], sup_env["warehouse_id"], sup_env["sku_id"],
                sup_env["po_id"], qty=5, created_at=_at(p1t))
    stmt2 = create_supplier_statement(
        session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
        code=None, period_from=p1f, period_to=p1t,
    )
    assert stmt2.amount == Decimal("75")  # 仅新流水 5 × 15
    assert stmt2.items[0].received_qty == 5


def test_sup_full_period_statement_blocks_later(session, sup_env):
    """全量对账单（无期间）之后，再生成任意期间单 → 拒绝。"""
    p1f, p1t = _last_month()
    _mk_stockin(session, sup_env["tenant_id"], sup_env["warehouse_id"], sup_env["sku_id"],
                sup_env["po_id"], qty=10, created_at=_at(p1t))
    create_supplier_statement(
        session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
        code=None, period_from=None, period_to=None,
    )
    with pytest.raises(ValueError, match="已在其他对账单"):
        create_supplier_statement(
            session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
            code=None, period_from=p1f, period_to=p1t,
        )


def test_sup_no_stockin_in_period(session, sup_env):
    """空期间 → 该期间无入库记录（先于冲突检测报错）。"""
    p1f, p1t = _last_month()
    with pytest.raises(ValueError, match="该期间无入库记录"):
        create_supplier_statement(
            session, tenant_id=sup_env["tenant_id"], supplier_id=sup_env["supplier_id"],
            code=None, period_from=p1f, period_to=p1t,
        )
