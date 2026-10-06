"""P2-20：MRP 可用库存过滤停用仓 + 采购建议按供应商分单 回归测试

背景（审计 Part 1 #7）：
- `sum_stock_qty_by_sku_ids` 汇总库存不过滤启用仓，停用仓库存被当作可用量；
- `convert_shortage_to_purchase_order` 只能把所有缺料项挂到单一供应商。

修复：
- 库存汇总 join Warehouse 并过滤 is_active（MRP/齐套/领料可用量口径统一）；
- convert 的 supplier_id 改为可选：指定 = 合并一张（原行为），留空 = 按物料默认供应商自动分单；
- 返回统一 {"orders": [...]}，指定单一供应商时保留顶层 code/purchase_order_id（兼容旧契约）。
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.crud.warehouse import sum_stock_qty_by_sku_ids
from app.models.material import Material, Supplier
from app.models.mrp import MrpDemand, MrpRun
from app.models.purchase import PurchaseOrder, PurchaseOrderItem
from app.models.sku import Sku
from app.models.warehouse import Stock, Warehouse
from app.services.mrp_suggestion import convert_shortage_to_purchase_order


# ---------------- 造数 ----------------

def _mk_warehouse(session, tenant_id, code, is_active=True):
    w = Warehouse(tenant_id=tenant_id, code=code, name=code, is_active=is_active)
    session.add(w)
    session.flush()
    return w


def _mk_stock(session, tenant_id, warehouse_id, sku_id, qty):
    s = Stock(tenant_id=tenant_id, warehouse_id=warehouse_id, sku_id=sku_id, qty=qty)
    session.add(s)
    session.flush()
    return s


def _mk_sku(session, tenant_id, product_id, code):
    s = Sku(tenant_id=tenant_id, product_id=product_id, code=code, name=code, is_active=True)
    session.add(s)
    session.flush()
    return s


def _mk_supplier(session, tenant_id, code):
    s = Supplier(tenant_id=tenant_id, code=code, name=code)
    session.add(s)
    session.flush()
    return s


def _mk_material(session, tenant_id, sku_id, supplier_id, code):
    m = Material(tenant_id=tenant_id, code=code, name=code, sku_id=sku_id, supplier_id=supplier_id)
    session.add(m)
    session.flush()
    return m


def _mk_run(session, tenant_id, code="MRP-T01"):
    r = MrpRun(tenant_id=tenant_id, code=code, status="done", scope="all")
    session.add(r)
    session.flush()
    return r


def _mk_demand(session, tenant_id, run_id, sku_id, shortage=5):
    d = MrpDemand(
        tenant_id=tenant_id, run_id=run_id, sku_id=sku_id,
        required_qty=shortage + 10, in_stock_qty=10, on_order_qty=0,
        shortage_qty=shortage, suggestion="purchase",
    )
    session.add(d)
    session.flush()
    return d


def _po_items(session, po_id):
    return session.scalars(
        select(PurchaseOrderItem).where(PurchaseOrderItem.order_id == po_id)
    ).all()


# ---------------- 库存过滤停用仓 ----------------

def test_stock_sum_excludes_inactive_warehouse(session, tenant, sku, product):
    """启用仓 10 + 停用仓 5 → 可用量只算 10；仅停用仓有货的 SKU 不出现（按 0 计）。"""
    wa = _mk_warehouse(session, tenant.id, "WH-A", True)
    wi = _mk_warehouse(session, tenant.id, "WH-I", False)
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")

    _mk_stock(session, tenant.id, wa.id, sku.id, 10)
    _mk_stock(session, tenant.id, wi.id, sku.id, 5)
    _mk_stock(session, tenant.id, wi.id, sku2.id, 7)  # 仅停用仓有货

    m = sum_stock_qty_by_sku_ids(session, tenant.id, [sku.id, sku2.id])
    assert m[sku.id] == 10
    assert m.get(sku2.id, 0) == 0


def test_stock_sum_multi_warehouse_active_only(session, tenant, sku):
    """多启用仓正常累加（不误伤正常口径）。"""
    w1 = _mk_warehouse(session, tenant.id, "WH-1", True)
    w2 = _mk_warehouse(session, tenant.id, "WH-2", True)
    w3 = _mk_warehouse(session, tenant.id, "WH-3", False)
    _mk_stock(session, tenant.id, w1.id, sku.id, 3)
    _mk_stock(session, tenant.id, w2.id, sku.id, 4)
    _mk_stock(session, tenant.id, w3.id, sku.id, 100)
    m = sum_stock_qty_by_sku_ids(session, tenant.id, [sku.id])
    assert m[sku.id] == 7


# ---------------- 按供应商分单 ----------------

def test_convert_with_supplier_merges_all(session, tenant, sku, product):
    """指定供应商：全部缺料合并一张（原行为），顶层兼容字段保留。"""
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU-S2")
    sup_default = _mk_supplier(session, tenant.id, "SUP-DEF")
    sup_target = _mk_supplier(session, tenant.id, "SUP-TGT")
    _mk_material(session, tenant.id, sku.id, sup_default.id, "M-S1")
    _mk_material(session, tenant.id, sku2.id, sup_default.id, "M-S2")
    run = _mk_run(session, tenant.id)
    _mk_demand(session, tenant.id, run.id, sku.id, shortage=5)
    _mk_demand(session, tenant.id, run.id, sku2.id, shortage=8)

    out = convert_shortage_to_purchase_order(session, tenant.id, run.id, supplier_id=sup_target.id)
    assert len(out["orders"]) == 1
    order = out["orders"][0]
    assert order["supplier_id"] == sup_target.id
    assert order["item_count"] == 2
    assert out["code"] == order["code"]  # 旧契约兼容
    assert out["purchase_order_id"] == order["purchase_order_id"]

    po = session.get(PurchaseOrder, order["purchase_order_id"])
    assert po is not None and po.supplier_id == sup_target.id
    assert len(_po_items(session, po.id)) == 2


def test_convert_auto_split_by_material_supplier(session, tenant, sku, product):
    """不指定供应商：按物料默认供应商自动分单（2 供应商 → 2 张，各含 1 明细）。"""
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU-A2")
    sup1 = _mk_supplier(session, tenant.id, "SUP-1")
    sup2 = _mk_supplier(session, tenant.id, "SUP-2")
    _mk_material(session, tenant.id, sku.id, sup1.id, "M-A1")
    _mk_material(session, tenant.id, sku2.id, sup2.id, "M-A2")
    run = _mk_run(session, tenant.id, "MRP-T02")
    _mk_demand(session, tenant.id, run.id, sku.id, shortage=5)
    _mk_demand(session, tenant.id, run.id, sku2.id, shortage=3)

    out = convert_shortage_to_purchase_order(session, tenant.id, run.id)
    assert len(out["orders"]) == 2
    by_sup = {o["supplier_id"]: o for o in out["orders"]}
    assert set(by_sup.keys()) == {sup1.id, sup2.id}
    assert by_sup[sup1.id]["item_count"] == 1
    assert by_sup[sup2.id]["item_count"] == 1
    assert "code" not in out  # 分单场景无顶层兼容字段

    for o in out["orders"]:
        po = session.get(PurchaseOrder, o["purchase_order_id"])
        assert po is not None and po.supplier_id == o["supplier_id"]
        assert len(_po_items(session, po.id)) == 1


def test_convert_skips_non_shortage_demands(session, tenant, sku):
    """shortage=0 的需求不参与转换（只转真正缺料项）。"""
    sup1 = _mk_supplier(session, tenant.id, "SUP-ONLY")
    _mk_material(session, tenant.id, sku.id, sup1.id, "M-ONLY")
    run = _mk_run(session, tenant.id, "MRP-T03")
    _mk_demand(session, tenant.id, run.id, sku.id, shortage=0)

    with pytest.raises(ValueError, match="没有缺料项"):
        convert_shortage_to_purchase_order(session, tenant.id, run.id)


def test_convert_material_without_supplier_rejected(session, tenant, sku):
    """自动分单时物料未绑定默认供应商 → 明确报错（引导人工指定或先维护物料）。"""
    _mk_material(session, tenant.id, sku.id, None, "M-NOSUP")
    run = _mk_run(session, tenant.id, "MRP-T04")
    _mk_demand(session, tenant.id, run.id, sku.id, shortage=2)

    with pytest.raises(ValueError, match="未绑定默认供应商"):
        convert_shortage_to_purchase_order(session, tenant.id, run.id)


def test_convert_invalid_supplier_rejected(session, tenant, sku):
    """显式指定不存在的供应商 → 报错。"""
    _mk_material(session, tenant.id, sku.id, None, "M-X")
    run = _mk_run(session, tenant.id, "MRP-T05")
    _mk_demand(session, tenant.id, run.id, sku.id, shortage=2)

    with pytest.raises(ValueError, match="供应商不存在"):
        convert_shortage_to_purchase_order(session, tenant.id, run.id, supplier_id=99999)
