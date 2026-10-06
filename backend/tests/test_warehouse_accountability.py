"""发货/外协发料收回仓库可追溯（P1-8）回归测试

背景：发货确认时后端自动取"最低 ID 启用仓"扣库存，发货单不记录出库仓；
外协发料/收货仅累加台账 sent_qty/received_qty，完全不碰库存，库存责任无法追溯。

修复：
- shipments.warehouse_id：发货单显式指定仓库；未指定（历史单据）发货时回退默认仓并回写
- 外协发料/收货可选 warehouse_id：指定时同步扣/加库存并写 subcontract_out/in 流水；
  不传保持纯台账（向后兼容）

覆盖：
- 创建发货单：带仓库落库 / 非法仓库 400
- 发货：从指定仓扣减（其他仓不动）/ 历史单据回退默认仓并回写
- 发货：指定仓库存不足 → 400 且库存与单据状态不变
- 外协发料：带仓库扣库存 + subcontract_out 流水 + 日志记仓
- 外协发料：不带仓库保持纯台账（库存不变）
- 外协发料：库存不足 → 400 且 sent_qty 不累加
- 外协收货：带仓库入库 + subcontract_in 流水 + 日志记仓
"""
from __future__ import annotations

import itertools

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.subcontract.router import router as subcontract_router
from app.api.admin.warehouse.shipments import router as shipments_router
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.material import Supplier
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment
from app.models.subcontract import SubcontractOrder, SubcontractOrderItem, SubcontractSendLog
from app.models.warehouse import Stock, StockLog, Warehouse

_counter = itertools.count(1)


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(shipments_router, prefix="/admin/warehouse")
    app.include_router(subcontract_router, prefix="/admin/subcontract")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: [
        "order.manage", "subcontract.manage", "warehouse.manage",
    ]
    return TestClient(app)


@pytest.fixture()
def wh_a(session, tenant):
    w = Warehouse(tenant_id=tenant.id, code="WH-A", name="一号仓", is_active=True)
    session.add(w)
    session.flush()
    return w


@pytest.fixture()
def wh_b(session, tenant):
    w = Warehouse(tenant_id=tenant.id, code="WH-B", name="二号仓", is_active=True)
    session.add(w)
    session.flush()
    return w


def _mk_stock(session, tenant_id, wh_id, sku_id, qty) -> Stock:
    s = Stock(tenant_id=tenant_id, warehouse_id=wh_id, sku_id=sku_id, qty=qty)
    session.add(s)
    session.flush()
    return s


@pytest.fixture()
def order(session, tenant, customer, sku):
    o = Order(tenant_id=tenant.id, customer_id=customer.id, code="SO-P18-1", status="confirmed")
    session.add(o)
    session.flush()
    session.add(OrderItem(
        tenant_id=tenant.id, order_id=o.id, line_no=1, sku_id=sku.id, qty=100,
        unit_price=10, subtotal=1000,
    ))
    session.flush()
    return o


@pytest.fixture()
def sc(session, tenant, sku):
    """委外单（明细 qty=10）。"""
    n = next(_counter)
    sup = Supplier(tenant_id=tenant.id, code=f"SUP-{n}", name=f"供应商{n}")
    session.add(sup)
    session.flush()
    order_ = SubcontractOrder(tenant_id=tenant.id, supplier_id=sup.id, code=f"SC-P18-{n}")
    session.add(order_)
    session.flush()
    item = SubcontractOrderItem(tenant_id=tenant.id, order_id=order_.id, sku_id=sku.id, qty=10)
    session.add(item)
    session.flush()
    return order_, item


def _create_shipment(client, order_id, code, sku_id, qty=10, warehouse_id=None):
    payload = {
        "order_id": order_id,
        "code": code,
        "items": [{"sku_id": sku_id, "qty": qty}],
    }
    if warehouse_id is not None:
        payload["warehouse_id"] = warehouse_id
    return client.post("/admin/warehouse/shipments", json=payload)


def _stock_qty(session, tenant_id, wh_id, sku_id) -> int:
    s = session.scalar(select(Stock).where(
        Stock.tenant_id == tenant_id, Stock.warehouse_id == wh_id, Stock.sku_id == sku_id,
    ))
    return int(s.qty) if s else 0


# ---------------- 发货仓库 ----------------

def test_create_shipment_with_warehouse(api, session, tenant, sku, order, wh_b):
    """创建发货单带仓库 → 落库；非法仓库 → 400。"""
    r = _create_shipment(api, order.id, "SH-P18-1", sku.id, warehouse_id=wh_b.id)
    assert r.status_code == 200, r.text
    s = session.scalar(select(Shipment).where(Shipment.code == "SH-P18-1"))
    assert s.warehouse_id == wh_b.id

    r2 = _create_shipment(api, order.id, "SH-P18-2", sku.id, warehouse_id=999999)
    assert r2.status_code == 400


def test_ship_from_specified_warehouse(api, session, tenant, sku, order, wh_a, wh_b):
    """发货从指定仓扣减：目标仓 -10、其他仓不动、流水 ship_out、单据记仓。"""
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 100)
    _mk_stock(session, tenant.id, wh_b.id, sku.id, 100)

    r = _create_shipment(api, order.id, "SH-P18-3", sku.id, qty=10, warehouse_id=wh_b.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]
    r2 = api.post(f"/admin/warehouse/shipments/{sid}/ship")
    assert r2.status_code == 200, r2.text

    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_b.id, sku.id) == 90  # 指定仓扣减
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 100  # 其他仓不动
    log = session.scalar(select(StockLog).where(StockLog.biz_type == "ship_out"))
    assert log is not None and log.change_qty == -10 and log.warehouse_id == wh_b.id
    s = session.scalar(select(Shipment).where(Shipment.code == "SH-P18-3"))
    assert s.warehouse_id == wh_b.id


def test_ship_legacy_fallback_default_and_write_back(api, session, tenant, sku, order, wh_a, wh_b):
    """历史单据（无仓库）→ 回退默认仓（最低 ID）扣减并回写 warehouse_id。"""
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 50)
    _mk_stock(session, tenant.id, wh_b.id, sku.id, 50)

    r = _create_shipment(api, order.id, "SH-P18-4", sku.id, qty=5)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]
    r2 = api.post(f"/admin/warehouse/shipments/{sid}/ship")
    assert r2.status_code == 200, r2.text

    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 45  # 默认仓（wh_a id 更小）
    assert _stock_qty(session, tenant.id, wh_b.id, sku.id) == 50
    s = session.scalar(select(Shipment).where(Shipment.code == "SH-P18-4"))
    assert s.warehouse_id == wh_a.id  # 回写实际出库仓


def test_ship_insufficient_stock_rejected(api, session, tenant, sku, order, wh_a):
    """指定仓库存不足 → 400，库存与单据状态不变。"""
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 5)
    r = _create_shipment(api, order.id, "SH-P18-5", sku.id, qty=10, warehouse_id=wh_a.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]

    r2 = api.post(f"/admin/warehouse/shipments/{sid}/ship")
    assert r2.status_code == 400
    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 5
    s = session.scalar(select(Shipment).where(Shipment.code == "SH-P18-5"))
    assert s.status == "pending"


# ---------------- 外协发料/收货 ----------------

def test_subcontract_send_with_warehouse(api, session, tenant, sku, sc, wh_a):
    """发料指定仓库 → 扣库存 + subcontract_out 流水 + 日志记仓。"""
    sco, item = sc
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 100)

    r = api.post(f"/admin/subcontract/{sco.id}/send", json={
        "sends": [{"item_id": item.id, "qty": 4}], "warehouse_id": wh_a.id,
    })
    assert r.status_code == 200, r.text
    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 96
    log = session.scalar(select(SubcontractSendLog).where(SubcontractSendLog.order_id == sco.id))
    assert log.warehouse_id == wh_a.id and log.qty == 4
    sledger = session.scalar(select(StockLog).where(StockLog.biz_type == "subcontract_out"))
    assert sledger is not None and sledger.change_qty == -4 and sledger.warehouse_id == wh_a.id
    session.refresh(item)
    assert item.sent_qty == 4


def test_subcontract_send_without_warehouse_legacy(api, session, tenant, sku, sc, wh_a):
    """发料不传仓库 → 纯台账（库存不变、日志无仓），向后兼容。"""
    sco, item = sc
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 100)

    r = api.post(f"/admin/subcontract/{sco.id}/send", json={
        "sends": [{"item_id": item.id, "qty": 4}],
    })
    assert r.status_code == 200, r.text
    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 100
    log = session.scalar(select(SubcontractSendLog).where(SubcontractSendLog.order_id == sco.id))
    assert log.warehouse_id is None
    session.refresh(item)
    assert item.sent_qty == 4


def test_subcontract_send_insufficient_stock_rejected(api, session, tenant, sku, sc, wh_a):
    """发料指定仓库库存不足 → 400 且 sent_qty 不累加、无日志。"""
    sco, item = sc
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 2)

    r = api.post(f"/admin/subcontract/{sco.id}/send", json={
        "sends": [{"item_id": item.id, "qty": 5}], "warehouse_id": wh_a.id,
    })
    assert r.status_code == 400
    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 2
    assert session.scalars(
        select(SubcontractSendLog).where(SubcontractSendLog.order_id == sco.id)
    ).all() == []
    session.refresh(item)
    assert (item.sent_qty or 0) == 0


def test_subcontract_receive_with_warehouse(api, session, tenant, sku, sc, wh_a, wh_b):
    """收货指定仓库 → 入库 + subcontract_in 流水 + 日志记仓。"""
    sco, item = sc
    _mk_stock(session, tenant.id, wh_a.id, sku.id, 100)
    # 先发料（纯台账），使状态进入 sent
    r0 = api.post(f"/admin/subcontract/{sco.id}/send", json={
        "sends": [{"item_id": item.id, "qty": 10}],
    })
    assert r0.status_code == 200, r0.text

    r = api.post(f"/admin/subcontract/{sco.id}/receive", json={
        "item_id": item.id, "qty": 3, "warehouse_id": wh_b.id,
    })
    assert r.status_code == 200, r.text
    session.expire_all()
    assert _stock_qty(session, tenant.id, wh_b.id, sku.id) == 3  # 收入指定仓
    assert _stock_qty(session, tenant.id, wh_a.id, sku.id) == 100
    rlog = session.scalar(select(StockLog).where(StockLog.biz_type == "subcontract_in"))
    assert rlog is not None and rlog.change_qty == 3 and rlog.warehouse_id == wh_b.id
    session.refresh(item)
    assert item.received_qty == 3
