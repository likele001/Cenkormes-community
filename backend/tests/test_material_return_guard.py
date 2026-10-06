"""退料超领护栏补强（P1-16）回归测试

背景：`confirm_return` 原无超领护栏（issue_item_id 可选且不校验退料量 ≤ 已领量）→ 库存虚增。
基础护栏（单次/累计超领、跨单明细）已由 tests/test_stock_guard.py 覆盖；
本文件补强并锁定以下场景：

- 关联「未实际领料」的领料单（draft / cancelled）退料 → 拒绝（未扣过库存，退料会凭空增库存）
- 跨租户领料明细 → 创建即拒绝，且不改动对方数据
- 累计退料的精确边界（6 + 4 = 10 允许，再退 1 拒绝）+ 库存与流水口径
- 未关联领料明细的自由退料（盘盈退回等）→ 不受联动护栏，正常入库
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.crud.material_issue import cancel_issue, confirm_return, create_issue, create_return, issue_materials
from app.crud.warehouse import adjust_stock, get_stock
from app.models.material import Material
from app.models.product import Product
from app.models.sku import Sku
from app.models.tenant import Tenant
from app.models.warehouse import StockLog, Warehouse


def _mk_warehouse(db, tenant: Tenant, code: str = "WHG1") -> Warehouse:
    wh = Warehouse(tenant_id=tenant.id, code=code, name=code)
    db.add(wh)
    db.flush()
    return wh


def _mk_material(db, tenant: Tenant, sku, code: str = "MG1") -> Material:
    m = Material(tenant_id=tenant.id, code=code, name=code, sku_id=sku.id)
    db.add(m)
    db.flush()
    return m


def _stock_logs(db, tenant_id: int, warehouse_id: int, sku_id: int):
    return db.scalars(
        select(StockLog)
        .where(StockLog.tenant_id == tenant_id, StockLog.warehouse_id == warehouse_id, StockLog.sku_id == sku_id)
        .order_by(StockLog.id)
    ).all()


def test_return_from_draft_issue_rejected(session, tenant, sku):
    """关联 draft（未领料）领料单退料 → 拒绝，库存不变。"""
    wh = _mk_warehouse(session, tenant)
    m = _mk_material(session, tenant, sku)
    issue = create_issue(
        session, tenant.id, "ISSUE-D1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 5}],
    )
    # 不执行 issue_materials，保持 draft
    ii = issue.items[0]
    ret = create_return(
        session, tenant.id, "RET-D1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 2, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError, match="未实际领料"):
        confirm_return(session, ret=ret)
    assert ret.status == "draft"
    s = get_stock(session, tenant.id, wh.id, sku.id)
    assert s is None or s.qty == 0
    assert _stock_logs(session, tenant.id, wh.id, sku.id) == []


def test_return_from_cancelled_issue_rejected(session, tenant, sku):
    """关联 cancelled（已取消）领料单退料 → 拒绝。"""
    wh = _mk_warehouse(session, tenant, "WHG2")
    m = _mk_material(session, tenant, sku, "MG2")
    issue = create_issue(
        session, tenant.id, "ISSUE-C1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 3}],
    )
    cancel_issue(session, issue=issue)
    ii = issue.items[0]
    ret = create_return(
        session, tenant.id, "RET-C1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 1, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError, match="未实际领料"):
        confirm_return(session, ret=ret)
    assert ret.status == "draft"


def test_return_cross_tenant_issue_item_rejected(session, tenant, sku):
    """他租户领料明细 → 创建即拒绝，且不改动他租户数据。"""
    other = Tenant(code="OTG1", name="他厂G1")
    session.add(other)
    session.flush()
    # 他租户自备产品/型号/仓库/物料
    other_product = Product(tenant_id=other.id, code="OP-OTG", name="他厂产品", category="电子", unit="个", is_active=True)
    session.add(other_product)
    session.flush()
    other_sku = Sku(tenant_id=other.id, product_id=other_product.id, code="OSKU-OTG", name="他厂型号", is_active=True)
    session.add(other_sku)
    session.flush()
    other_wh = _mk_warehouse(session, other, "WH-OTG")
    other_m = _mk_material(session, other, other_sku, "MG-OTG")
    other_issue = create_issue(
        session, other.id, "ISSUE-OTG", other_wh.id,
        [{"material_id": other_m.id, "sku_id": other_sku.id, "qty": 5}],
    )
    other_ii = other_issue.items[0]

    wh = _mk_warehouse(session, tenant, "WHG3")
    m = _mk_material(session, tenant, sku, "MG3")
    with pytest.raises(ValueError):
        create_return(
            session, tenant.id, "RET-X1", wh.id,
            [{"material_id": m.id, "sku_id": sku.id, "qty": 1, "issue_item_id": other_ii.id}],
        )
    # 他租户数据未被改动
    assert other_issue.status == "draft"


def test_return_accumulate_exact_boundary(session, tenant, sku):
    """累计退料精确边界：6 + 4 = 10（已领）允许，再退 1 拒绝；库存/流水口径正确。"""
    wh = _mk_warehouse(session, tenant, "WHG4")
    m = _mk_material(session, tenant, sku, "MG4")
    adjust_stock(session, tenant.id, wh.id, sku.id, 10, "manual")
    issue = create_issue(
        session, tenant.id, "ISSUE-B1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 10}],
    )
    issue_materials(session, issue=issue)
    ii = issue.items[0]
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 0

    ret1 = create_return(
        session, tenant.id, "RET-B1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 6, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    confirm_return(session, ret=ret1)
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 6

    ret2_over = create_return(
        session, tenant.id, "RET-B2", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 5, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError, match="超过已领数量"):
        confirm_return(session, ret=ret2_over)
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 6

    ret2 = create_return(
        session, tenant.id, "RET-B3", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 4, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    confirm_return(session, ret=ret2)
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 10

    ret3 = create_return(
        session, tenant.id, "RET-B4", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 1, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError, match="超过已领数量"):
        confirm_return(session, ret=ret3)
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 10

    logs = _stock_logs(session, tenant.id, wh.id, sku.id)
    assert [l.change_qty for l in logs] == [10, -10, 6, 4]
    assert [l.balance_qty for l in logs] == [10, 0, 6, 10]


def test_free_return_without_issue_item_allowed(session, tenant, sku):
    """自由退料（未关联领料明细，如盘盈退回）：不受联动护栏，正常入库。"""
    wh = _mk_warehouse(session, tenant, "WHG5")
    m = _mk_material(session, tenant, sku, "MG5")
    ret = create_return(
        session, tenant.id, "RET-F1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 3}],
    )
    confirm_return(session, ret=ret)
    assert ret.status == "returned"
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 3
