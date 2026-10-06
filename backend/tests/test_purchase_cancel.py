"""P2-23：采购单作废 reason 留痕 + 部分收货作废护栏 回归测试

背景（审计 2.3）：
- `cancel` 无 reason 参数，作废原因无留痕；
- `partial_received`（已部分收货）状态可直接一键作废，不提示已入库事实。

修复：
- POST /purchase/orders/{id}/cancel 接受可选 body {reason}；
- partial_received 作废时 reason 必填（400），防止掩盖已收货事实；
- 作废原因写入 operation_logs.detail（reason=xxx）。
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.purchase import orders as purchase_orders
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.models.material import Material, Supplier
from app.models.operation_log import OperationLog
from app.models.purchase import PurchaseOrder, PurchaseOrderItem


def _mk_supplier(session, tenant_id):
    s = Supplier(tenant_id=tenant_id, code="SUP-CAN", name="作废测试供应商")
    session.add(s)
    session.flush()
    return s


def _mk_material(session, tenant_id, sku_id, supplier_id):
    m = Material(tenant_id=tenant_id, code="M-CAN", name="作废测试物料", sku_id=sku_id, supplier_id=supplier_id)
    session.add(m)
    session.flush()
    return m


def _mk_po(session, tenant_id, supplier_id, status="draft", code="PO-CAN"):
    po = PurchaseOrder(tenant_id=tenant_id, supplier_id=supplier_id, code=code, status=status)
    session.add(po)
    session.flush()
    return po


def _mk_po_item(session, tenant_id, order_id, material_id, qty=10):
    it = PurchaseOrderItem(
        tenant_id=tenant_id, order_id=order_id, material_id=material_id, qty=qty, unit_price=Decimal("10"),
    )
    session.add(it)
    session.flush()
    return it


@pytest.fixture()
def env(session, tenant, sku):
    """最小环境：供应商 + 物料（绑定 sku）。"""
    supplier = _mk_supplier(session, tenant.id)
    material = _mk_material(session, tenant.id, sku.id, supplier.id)
    return {"tenant_id": tenant.id, "supplier_id": supplier.id, "material_id": material.id}


@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(purchase_orders.router, prefix="/purchase")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["purchase.manage"]
    return TestClient(app)


def _cancel_log(session, tenant_id, po_id):
    return session.scalar(
        select(OperationLog).where(
            OperationLog.tenant_id == tenant_id,
            OperationLog.action == "cancel",
            OperationLog.object_id == po_id,
        )
    )


def test_cancel_draft_without_reason_ok(api, session, env):
    """draft（未确认）作废：reason 可选，无 body 亦可。"""
    po = _mk_po(session, env["tenant_id"], env["supplier_id"], status="draft", code="PO-CAN-1")
    _mk_po_item(session, env["tenant_id"], po.id, env["material_id"])
    r = api.post(f"/purchase/{po.id}/cancel")
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "canceled"
    log = _cancel_log(session, env["tenant_id"], po.id)
    assert log is not None
    assert "status=draft->canceled" in log.detail
    assert "reason=" not in log.detail


def test_cancel_confirmed_with_reason_logged(api, session, env):
    """confirmed 作废：reason 写入 operation_logs.detail。"""
    po = _mk_po(session, env["tenant_id"], env["supplier_id"], status="confirmed", code="PO-CAN-2")
    _mk_po_item(session, env["tenant_id"], po.id, env["material_id"])
    r = api.post(f"/purchase/{po.id}/cancel", json={"reason": "供应商缺货无法交付"})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "canceled"
    log = _cancel_log(session, env["tenant_id"], po.id)
    assert "status=confirmed->canceled" in log.detail
    assert "reason=供应商缺货无法交付" in log.detail


def test_cancel_partial_received_requires_reason(api, session, env):
    """partial_received 作废：reason 缺失/空白 → 400，状态不变，不落日志。"""
    po = _mk_po(session, env["tenant_id"], env["supplier_id"], status="partial_received", code="PO-CAN-3")
    _mk_po_item(session, env["tenant_id"], po.id, env["material_id"])

    r = api.post(f"/purchase/{po.id}/cancel")
    assert r.status_code == 400
    assert "必须填写原因" in r.json()["detail"]

    r2 = api.post(f"/purchase/{po.id}/cancel", json={"reason": "   "})
    assert r2.status_code == 400

    session.refresh(po)
    assert po.status == "partial_received"
    assert _cancel_log(session, env["tenant_id"], po.id) is None


def test_cancel_partial_received_with_reason_ok(api, session, env):
    """partial_received 作废：填原因后允许，状态变化 + reason 留痕。"""
    po = _mk_po(session, env["tenant_id"], env["supplier_id"], status="partial_received", code="PO-CAN-4")
    _mk_po_item(session, env["tenant_id"], po.id, env["material_id"])
    r = api.post(f"/purchase/{po.id}/cancel", json={"reason": "剩余数量供应商无法供货"})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "canceled"
    log = _cancel_log(session, env["tenant_id"], po.id)
    assert "status=partial_received->canceled" in log.detail
    assert "reason=剩余数量供应商无法供货" in log.detail


def test_cancel_invalid_status_rejected(api, session, env):
    """已作废状态 → 400（状态机守卫保持）。"""
    po = _mk_po(session, env["tenant_id"], env["supplier_id"], status="canceled", code="PO-CAN-5")
    _mk_po_item(session, env["tenant_id"], po.id, env["material_id"])
    r = api.post(f"/purchase/{po.id}/cancel", json={"reason": "x"})
    assert r.status_code == 400
    assert "状态不允许作废" in r.json()["detail"]
