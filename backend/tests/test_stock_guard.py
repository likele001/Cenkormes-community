"""库存护栏（P0-3）回归测试

覆盖：
- adjust_stock：负库存拒绝、正常出入库与流水
- create_issue：跨租户仓库归属拒绝
- issue_materials：库存不足拒绝
- confirm_return：退料超领护栏（累计口径）
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.crud.material_issue import confirm_return, create_issue, create_return, issue_materials
from app.crud.warehouse import adjust_stock, get_stock
from app.models.material import Material
from app.models.tenant import Tenant
from app.models.warehouse import StockLog, Warehouse


def _mk_warehouse(db, tenant: Tenant, code: str = "WH1") -> Warehouse:
    wh = Warehouse(tenant_id=tenant.id, code=code, name=code)
    db.add(wh)
    db.flush()
    return wh


def _mk_material(db, tenant: Tenant, sku, code: str = "M1") -> Material:
    m = Material(tenant_id=tenant.id, code=code, name=code, sku_id=sku.id)
    db.add(m)
    db.flush()
    return m


def test_adjust_stock_rejects_negative(session, tenant, sku):
    """出库超过现有库存 → 拒绝，库存不变。"""
    wh = _mk_warehouse(session, tenant)
    adjust_stock(session, tenant.id, wh.id, sku.id, 5, "manual")
    with pytest.raises(ValueError):
        adjust_stock(session, tenant.id, wh.id, sku.id, -6, "manual")
    s = get_stock(session, tenant.id, wh.id, sku.id)
    assert s.qty == 5


def test_adjust_stock_ok_and_log(session, tenant, sku):
    """正常出入库：余额正确、流水按序落库。"""
    wh = _mk_warehouse(session, tenant)
    adjust_stock(session, tenant.id, wh.id, sku.id, 10, "manual")
    adjust_stock(session, tenant.id, wh.id, sku.id, -4, "manual")
    s = get_stock(session, tenant.id, wh.id, sku.id)
    assert s.qty == 6
    logs = session.scalars(
        select(StockLog)
        .where(StockLog.tenant_id == tenant.id, StockLog.warehouse_id == wh.id, StockLog.sku_id == sku.id)
        .order_by(StockLog.id)
    ).all()
    assert [l.change_qty for l in logs] == [10, -4]
    assert [l.balance_qty for l in logs] == [10, 6]


def test_create_issue_cross_tenant_warehouse_rejected(session, tenant, sku):
    """领料单引用他租户仓库 → 拒绝。"""
    other = Tenant(code="OT1", name="他厂")
    session.add(other)
    session.flush()
    other_wh = _mk_warehouse(session, other, "WH-OTHER")
    m = _mk_material(session, tenant, sku)
    with pytest.raises(ValueError):
        create_issue(
            session, tenant.id, "ISSUE-1", other_wh.id,
            [{"material_id": m.id, "sku_id": sku.id, "qty": 1}],
        )


def test_issue_insufficient_stock(session, tenant, sku):
    """领料出库时库存不足 → 拒绝。"""
    wh = _mk_warehouse(session, tenant)
    m = _mk_material(session, tenant, sku)
    issue = create_issue(
        session, tenant.id, "ISSUE-2", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 3}],
    )
    with pytest.raises(ValueError):
        issue_materials(session, issue=issue)


def test_return_over_issue_rejected(session, tenant, sku):
    """退料超领护栏：单次超领拒绝；累计超领拒绝。"""
    wh = _mk_warehouse(session, tenant)
    m = _mk_material(session, tenant, sku)
    adjust_stock(session, tenant.id, wh.id, sku.id, 5, "manual")
    issue = create_issue(
        session, tenant.id, "ISSUE-3", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 5}],
    )
    issue_materials(session, issue=issue)
    ii = issue.items[0]

    ret_over = create_return(
        session, tenant.id, "RET-1", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 6, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError):
        confirm_return(session, ret=ret_over)

    ret_ok = create_return(
        session, tenant.id, "RET-2", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 5, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    confirm_return(session, ret=ret_ok)

    ret_again = create_return(
        session, tenant.id, "RET-3", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 1, "issue_item_id": ii.id}],
        issue_id=issue.id,
    )
    with pytest.raises(ValueError):
        confirm_return(session, ret=ret_again)


def test_return_wrong_issue_item_rejected(session, tenant, sku):
    """退料明细指向不属于该领料单的领料明细 → 创建即拒绝。"""
    other = Tenant(code="OT2", name="他厂2")
    session.add(other)
    session.flush()
    wh = _mk_warehouse(session, tenant)
    m = _mk_material(session, tenant, sku)
    issue = create_issue(
        session, tenant.id, "ISSUE-4", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 2}],
    )
    ii = issue.items[0]
    # 构造另一个领料单（同租户），用它的明细 id 给本单退料
    issue2 = create_issue(
        session, tenant.id, "ISSUE-5", wh.id,
        [{"material_id": m.id, "sku_id": sku.id, "qty": 2}],
    )
    ii2 = issue2.items[0]
    with pytest.raises(ValueError):
        create_return(
            session, tenant.id, "RET-4", wh.id,
            [{"material_id": m.id, "sku_id": sku.id, "qty": 1, "issue_item_id": ii2.id}],
            issue_id=issue.id,
        )
