"""发货取消端点（P4-31）回归测试

背景：审计发现发货单状态机 pending → shipped → signed 无取消/回滚途径，
模型中 cancelled 为死状态（超发护栏已剔除 cancelled，但无端点可达）。

修复：新增 POST /admin/warehouse/shipments/{id}/cancel：
- pending 直接取消（未扣库存）
- shipped 取消时逐项回滚库存 + 写 ship_cancel 冲销流水；订单无其它有效发货单时回退 confirmed
- signed 不可取消（400）；重复取消 400；写 operation_logs 留痕

覆盖：
- pending 取消：状态变更、库存不变、op log
- shipped 取消：库存回滚 + ship_cancel 流水 + 订单状态回退
- 存在其它有效发货单时订单状态保持
- signed 取消 400
- 重复取消 400
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.warehouse.shipments import router as shipments_router
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.operation_log import OperationLog
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment
from app.models.warehouse import Stock, StockLog, Warehouse


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(shipments_router, prefix="/admin/warehouse")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["order.manage", "warehouse.manage"]
    return TestClient(app)


@pytest.fixture()
def wh(session, tenant):
    w = Warehouse(tenant_id=tenant.id, code="WH-P31", name="发货仓", is_active=True)
    session.add(w)
    session.flush()
    return w


@pytest.fixture()
def order(session, tenant, customer, sku):
    o = Order(tenant_id=tenant.id, customer_id=customer.id, code="SO-P31-1", status="confirmed")
    session.add(o)
    session.flush()
    session.add(OrderItem(
        tenant_id=tenant.id, order_id=o.id, line_no=1, sku_id=sku.id, qty=100,
        unit_price=10, subtotal=1000,
    ))
    session.flush()
    return o


def _mk_stock(session, tenant_id, wh_id, sku_id, qty) -> Stock:
    s = Stock(tenant_id=tenant_id, warehouse_id=wh_id, sku_id=sku_id, qty=qty)
    session.add(s)
    session.flush()
    return s


def _create_shipment(client, order_id, code, sku_id, qty, warehouse_id):
    return client.post("/admin/warehouse/shipments", json={
        "order_id": order_id, "code": code, "warehouse_id": warehouse_id,
        "items": [{"sku_id": sku_id, "qty": qty}],
    })


def _stock_qty(session, tenant_id, wh_id, sku_id) -> int:
    s = session.scalar(select(Stock).where(
        Stock.tenant_id == tenant_id, Stock.warehouse_id == wh_id, Stock.sku_id == sku_id,
    ))
    return int(s.qty) if s else 0


def test_cancel_pending_ok(api, session, tenant, sku, order, wh):
    """pending 取消：状态置 cancelled，库存不变，无冲销流水，写 op log。"""
    _mk_stock(session, tenant.id, wh.id, sku.id, 50)
    r = _create_shipment(api, order.id, "SH-P31-1", sku.id, 10, wh.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]

    r2 = api.post(f"/admin/warehouse/shipments/{sid}/cancel")
    assert r2.status_code == 200, r2.text
    assert r2.json()["data"]["status"] == "cancelled"

    session.expire_all()
    assert _stock_qty(session, tenant.id, wh.id, sku.id) == 50  # 未发货不扣不加
    assert session.scalar(select(StockLog).where(StockLog.biz_type == "ship_cancel")) is None
    log = session.scalar(select(OperationLog).where(
        OperationLog.module == "warehouse",
        OperationLog.action == "cancel_shipment",
        OperationLog.object_id == sid,
    ))
    assert log is not None and "prev_status=pending" in (log.detail or "")


def test_cancel_shipped_rollback_stock_and_order(api, session, tenant, sku, order, wh):
    """shipped 取消：库存回滚 + ship_cancel 流水 + 订单状态回退 confirmed。"""
    _mk_stock(session, tenant.id, wh.id, sku.id, 100)
    r = _create_shipment(api, order.id, "SH-P31-2", sku.id, 10, wh.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]
    assert api.post(f"/admin/warehouse/shipments/{sid}/ship").status_code == 200

    session.expire_all()
    assert _stock_qty(session, tenant.id, wh.id, sku.id) == 90
    assert session.get(Order, order.id).status == "shipped"

    r2 = api.post(f"/admin/warehouse/shipments/{sid}/cancel")
    assert r2.status_code == 200, r2.text

    session.expire_all()
    assert _stock_qty(session, tenant.id, wh.id, sku.id) == 100  # 库存加回
    assert session.get(Shipment, sid).status == "cancelled"
    assert session.get(Order, order.id).status == "confirmed"  # 订单回退
    cancel_log = session.scalar(select(StockLog).where(StockLog.biz_type == "ship_cancel"))
    assert cancel_log is not None and cancel_log.change_qty == 10


def test_cancel_keeps_order_status_with_other_active(api, session, tenant, sku, order, wh):
    """存在其它有效发货单（shipped/signed）时，取消不把订单状态回退。"""
    _mk_stock(session, tenant.id, wh.id, sku.id, 100)
    r1 = _create_shipment(api, order.id, "SH-P31-3", sku.id, 10, wh.id)
    r2 = _create_shipment(api, order.id, "SH-P31-4", sku.id, 10, wh.id)
    assert r1.status_code == 200 and r2.status_code == 200, f"{r1.text} {r2.text}"
    sid1, sid2 = r1.json()["data"]["id"], r2.json()["data"]["id"]
    assert api.post(f"/admin/warehouse/shipments/{sid1}/ship").status_code == 200
    assert api.post(f"/admin/warehouse/shipments/{sid2}/ship").status_code == 200

    session.expire_all()
    assert session.get(Order, order.id).status == "shipped"

    assert api.post(f"/admin/warehouse/shipments/{sid1}/cancel").status_code == 200
    session.expire_all()
    assert session.get(Shipment, sid1).status == "cancelled"
    assert session.get(Shipment, sid2).status == "shipped"
    assert session.get(Order, order.id).status == "shipped"  # 仍有一单在途，不回退


def test_cancel_signed_400(api, session, tenant, sku, order, wh):
    """已签收的发货单不可取消（400），库存不回滚。"""
    _mk_stock(session, tenant.id, wh.id, sku.id, 100)
    r = _create_shipment(api, order.id, "SH-P31-5", sku.id, 10, wh.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]
    assert api.post(f"/admin/warehouse/shipments/{sid}/ship").status_code == 200
    assert api.post(f"/admin/warehouse/shipments/{sid}/sign").status_code == 200

    r2 = api.post(f"/admin/warehouse/shipments/{sid}/cancel")
    assert r2.status_code == 400
    session.expire_all()
    assert session.get(Shipment, sid).status == "signed"
    assert _stock_qty(session, tenant.id, wh.id, sku.id) == 90  # 库存不回滚


def test_cancel_twice_400(api, session, tenant, sku, order, wh):
    """重复取消 → 400。"""
    _mk_stock(session, tenant.id, wh.id, sku.id, 50)
    r = _create_shipment(api, order.id, "SH-P31-6", sku.id, 10, wh.id)
    assert r.status_code == 200, r.text
    sid = r.json()["data"]["id"]
    assert api.post(f"/admin/warehouse/shipments/{sid}/cancel").status_code == 200
    r2 = api.post(f"/admin/warehouse/shipments/{sid}/cancel")
    assert r2.status_code == 400
