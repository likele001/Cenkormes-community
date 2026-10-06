"""库存盘点闭环（P2-21）回归测试

背景：此前系统无盘点能力——库存只能随业务流水被动变动，无「账面快照 →
实盘录入 → 差异调账」闭环，账实不符无法识别与修正。

修复：新增 stock_checks / stock_check_items + /admin/warehouse/stock-checks
6 端点：建单（全盘快照该仓全部库存行 / 抽盘指定型号）→ 录入实盘 → 完成时
逐行 adjust_stock(diff) 并写 stock_check 流水（diff=0 不写），完成后锁定；
全流程写操作留痕（complete_stock_check）。

覆盖：
- 建单：全盘仅含本仓、抽盘（无库存型号按账面 0，支持盘盈）、无效型号/空仓报错
- 录入：负数、非本单明细、done 后改动均拒绝
- 完成：差异调库存 + stock_check 流水 balance=实盘、0 差异不写流水；
  盘盈建行；未录完/重复完成拒绝
- 删除：draft 可删、done 拒绝；跨租户隔离；列表过滤
- API：完整流程、无效仓库/日期格式/404s、done 删除 400、操作留痕
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.admin.warehouse import stock_checks as stock_checks_api
from app.core.deps import get_current_permissions, get_current_user, get_db
from app.crud.stock_check import (
    complete_check,
    create_check,
    delete_check,
    get_check_by_id,
    list_checks,
    update_items,
)
from app.crud.warehouse import get_stock
from app.models.operation_log import OperationLog  # noqa: F401  注册建表
from app.models.sku import Sku
from app.models.tenant import Tenant
from app.models.user import User  # noqa: F401
from app.models.warehouse import Stock, StockCheck, StockCheckItem, StockLog, Warehouse  # noqa: F401


def _mk_wh(db, tenant_id: int, code: str = "WH1") -> Warehouse:
    wh = Warehouse(tenant_id=tenant_id, code=code, name=code)
    db.add(wh)
    db.flush()
    return wh


def _mk_sku(db, tenant_id: int, product_id: int, code: str) -> Sku:
    s = Sku(tenant_id=tenant_id, product_id=product_id, code=code, name=code, is_active=True)
    db.add(s)
    db.flush()
    return s


def _mk_stock(db, tenant_id: int, warehouse_id: int, sku_id: int, qty: int) -> Stock:
    s = Stock(tenant_id=tenant_id, warehouse_id=warehouse_id, sku_id=sku_id, qty=qty)
    db.add(s)
    db.flush()
    return s


def _biz_logs(db, tenant_id: int, biz_id: int) -> list[StockLog]:
    return list(
        db.scalars(
            select(StockLog).where(
                StockLog.tenant_id == tenant_id,
                StockLog.biz_type == "stock_check",
                StockLog.biz_id == biz_id,
            )
        ).all()
    )


# ---------------- 建单 ----------------

def test_create_full_snapshot_only_this_warehouse(session, tenant, sku, product):
    wh = _mk_wh(session, tenant.id, "WH-A")
    wh2 = _mk_wh(session, tenant.id, "WH-B")
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    _mk_stock(session, tenant.id, wh.id, sku2.id, 5)
    _mk_stock(session, tenant.id, wh2.id, sku.id, 99)  # 另一仓库不入单

    ck = create_check(session, tenant.id, wh.id, "SCK001")
    assert ck.status == "draft"
    assert len(ck.items) == 2
    book = {it.sku_id: it.book_qty for it in ck.items}
    assert book == {sku.id: 10, sku2.id: 5}
    assert all(it.actual_qty is None and it.diff_qty is None for it in ck.items)


def test_create_partial_with_missing_stock_books_zero(session, tenant, sku, product):
    """抽盘：无库存记录的型号按账面 0 快照（支持盘盈）。"""
    wh = _mk_wh(session, tenant.id)
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)

    ck = create_check(session, tenant.id, wh.id, "SCK002", sku_ids=[sku.id, sku2.id])
    book = {it.sku_id: it.book_qty for it in ck.items}
    assert book == {sku.id: 10, sku2.id: 0}


def test_create_invalid_sku_rejected(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    with pytest.raises(ValueError, match="不存在"):
        create_check(session, tenant.id, wh.id, "SCK003", sku_ids=[sku.id, 999999])


def test_create_full_on_empty_warehouse_rejected(session, tenant):
    wh = _mk_wh(session, tenant.id)
    with pytest.raises(ValueError, match="无法全盘"):
        create_check(session, tenant.id, wh.id, "SCK004")


# ---------------- 录入实盘 ----------------

def test_update_items_rejects_negative_and_foreign_item(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    ck = create_check(session, tenant.id, wh.id, "SCK005")
    item = ck.items[0]

    with pytest.raises(ValueError, match="不属于该盘点单"):
        update_items(session, ck, [{"item_id": 999999, "actual_qty": 1}])
    with pytest.raises(ValueError, match="不能为负"):
        update_items(session, ck, [{"item_id": item.id, "actual_qty": -1}])

    update_items(session, ck, [{"item_id": item.id, "actual_qty": 8}])
    assert item.actual_qty == 8


def test_update_items_rejected_after_done(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    ck = create_check(session, tenant.id, wh.id, "SCK006")
    update_items(session, ck, [{"item_id": ck.items[0].id, "actual_qty": 10}])
    complete_check(session, tenant.id, ck)
    with pytest.raises(ValueError, match="不可修改"):
        update_items(session, ck, [{"item_id": ck.items[0].id, "actual_qty": 9}])


# ---------------- 完成：差异调账 ----------------

def test_complete_adjusts_stock_and_writes_logs_only_for_diff(session, tenant, sku, product):
    wh = _mk_wh(session, tenant.id)
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    _mk_stock(session, tenant.id, wh.id, sku2.id, 5)

    ck = create_check(session, tenant.id, wh.id, "SCK007")
    by_sku = {it.sku_id: it for it in ck.items}
    update_items(session, ck, [
        {"item_id": by_sku[sku.id].id, "actual_qty": 8},   # 盘亏 -2
        {"item_id": by_sku[sku2.id].id, "actual_qty": 5},  # 无差异
    ])
    complete_check(session, tenant.id, ck)

    assert ck.status == "done" and ck.completed_at is not None
    assert by_sku[sku.id].diff_qty == -2
    assert by_sku[sku2.id].diff_qty == 0

    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 8
    assert get_stock(session, tenant.id, wh.id, sku2.id).qty == 5

    logs = _biz_logs(session, tenant.id, ck.id)
    assert len(logs) == 1  # 0 差异行不写流水
    log = logs[0]
    assert log.sku_id == sku.id
    assert log.change_qty == -2
    assert log.balance_qty == 8  # 流水余额 = 实盘数
    assert "盘点调整" in (log.remark or "")


def test_complete_gain_creates_stock_row(session, tenant, sku, product):
    """盘盈：抽盘无库存型号录 3 → 建库存行 0 → 3 并写流水。"""
    wh = _mk_wh(session, tenant.id)
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)

    ck = create_check(session, tenant.id, wh.id, "SCK008", sku_ids=[sku2.id])
    update_items(session, ck, [{"item_id": ck.items[0].id, "actual_qty": 3}])
    complete_check(session, tenant.id, ck)

    assert ck.items[0].diff_qty == 3
    assert get_stock(session, tenant.id, wh.id, sku2.id).qty == 3
    logs = _biz_logs(session, tenant.id, ck.id)
    assert len(logs) == 1 and logs[0].change_qty == 3 and logs[0].balance_qty == 3


def test_complete_pending_rejected(session, tenant, sku, product):
    wh = _mk_wh(session, tenant.id)
    sku2 = _mk_sku(session, tenant.id, product.id, "SKU002")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    _mk_stock(session, tenant.id, wh.id, sku2.id, 5)

    ck = create_check(session, tenant.id, wh.id, "SCK009")
    update_items(session, ck, [{"item_id": ck.items[0].id, "actual_qty": 10}])
    with pytest.raises(ValueError, match="还有 1 行未录入"):
        complete_check(session, tenant.id, ck)


def test_complete_twice_rejected(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    ck = create_check(session, tenant.id, wh.id, "SCK010")
    update_items(session, ck, [{"item_id": ck.items[0].id, "actual_qty": 10}])
    complete_check(session, tenant.id, ck)
    with pytest.raises(ValueError, match="不可重复完成"):
        complete_check(session, tenant.id, ck)


# ---------------- 删除与隔离 ----------------

def test_delete_draft_ok_done_rejected(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)

    draft = create_check(session, tenant.id, wh.id, "SCK011")
    delete_check(session, draft)
    assert get_check_by_id(session, tenant.id, draft.id) is None

    done = create_check(session, tenant.id, wh.id, "SCK012")
    update_items(session, done, [{"item_id": done.items[0].id, "actual_qty": 10}])
    complete_check(session, tenant.id, done)
    with pytest.raises(ValueError, match="不可删除"):
        delete_check(session, done)


def test_cross_tenant_isolation(session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    ck = create_check(session, tenant.id, wh.id, "SCK013")

    t2 = Tenant(code="T2", name="租户2")
    session.add(t2)
    session.flush()
    assert get_check_by_id(session, t2.id, ck.id, with_items=True) is None
    assert list_checks(session, t2.id) == []


def test_list_filters(session, tenant, sku, product):
    wh = _mk_wh(session, tenant.id, "WH-A")
    wh2 = _mk_wh(session, tenant.id, "WH-B")
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    _mk_stock(session, tenant.id, wh2.id, sku.id, 7)

    c1 = create_check(session, tenant.id, wh.id, "SCK014")
    create_check(session, tenant.id, wh2.id, "SCK015")
    update_items(session, c1, [{"item_id": c1.items[0].id, "actual_qty": 10}])
    complete_check(session, tenant.id, c1)

    assert len(list_checks(session, tenant.id)) == 2
    assert [c.id for c in list_checks(session, tenant.id, warehouse_id=wh.id)] == [c1.id]
    assert [c.id for c in list_checks(session, tenant.id, status="draft")] != [c1.id]
    assert [c.id for c in list_checks(session, tenant.id, status="done")] == [c1.id]


# ---------------- API ----------------

@pytest.fixture()
def api(session, test_user):
    app = FastAPI()
    app.include_router(stock_checks_api.router, prefix="/admin/warehouse")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["warehouse.manage"]
    return TestClient(app)


def test_api_full_flow(api, session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)

    # 建单（全盘，自动编号 SCK 前缀）
    r = api.post("/admin/warehouse/stock-checks", json={"warehouse_id": wh.id, "remark": "月末盘点"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["code"].startswith("SCK")
    assert data["item_count"] == 1 and data["checked_count"] == 0
    ck_id = data["id"]
    item_id = data["items"][0]["id"]

    # 录入实盘
    r = api.put(f"/admin/warehouse/stock-checks/{ck_id}/items", json={"items": [{"item_id": item_id, "actual_qty": 7}]})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["checked_count"] == 1

    # 完成 → 库存 7 + 流水 + 留痕
    r = api.post(f"/admin/warehouse/stock-checks/{ck_id}/complete")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["status"] == "done" and data["diff_count"] == 1
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 7
    assert len(_biz_logs(session, tenant.id, ck_id)) == 1
    op = session.scalar(
        select(OperationLog).where(
            OperationLog.tenant_id == tenant.id,
            OperationLog.module == "warehouse",
            OperationLog.action == "complete_stock_check",
            OperationLog.object_id == ck_id,
        )
    )
    assert op is not None and "diff_count=1" in (op.detail or "")

    # 列表按状态过滤
    r = api.get("/admin/warehouse/stock-checks", params={"status": "done"})
    assert r.status_code == 200
    assert [x["id"] for x in r.json()["data"]["items"]] == [ck_id]


def _seed_and_complete(api, session, tenant, sku):
    """建单→录入→完成，返回 (wh, sku, ck_id)。供 400 路径测试复用。"""
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    r = api.post("/admin/warehouse/stock-checks", json={"warehouse_id": wh.id})
    ck_id = r.json()["data"]["id"]
    item_id = r.json()["data"]["items"][0]["id"]
    r = api.put(f"/admin/warehouse/stock-checks/{ck_id}/items", json={"items": [{"item_id": item_id, "actual_qty": 10}]})
    assert r.status_code == 200, r.text
    r = api.post(f"/admin/warehouse/stock-checks/{ck_id}/complete")
    assert r.status_code == 200, r.text
    return wh, sku, ck_id


def test_api_complete_twice_400(api, session, tenant, sku):
    """重复完成 → 400（400 路径会 rollback，故作为测试最后一步）。"""
    _wh, _sku, ck_id = _seed_and_complete(api, session, tenant, sku)
    r = api.post(f"/admin/warehouse/stock-checks/{ck_id}/complete")
    assert r.status_code == 400


def test_api_delete_done_400(api, session, tenant, sku):
    """已完成盘点删除 → 400（同上，作为测试最后一步）。"""
    _wh, _sku, ck_id = _seed_and_complete(api, session, tenant, sku)
    r = api.delete(f"/admin/warehouse/stock-checks/{ck_id}")
    assert r.status_code == 400
    assert "不可删除" in r.json()["detail"]


def test_api_create_invalid_warehouse_400(api, session, tenant):
    r = api.post("/admin/warehouse/stock-checks", json={"warehouse_id": 999999})
    assert r.status_code == 400
    assert "仓库不存在" in r.json()["detail"]


def test_api_create_bad_date_400(api, session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    r = api.post("/admin/warehouse/stock-checks", json={"warehouse_id": wh.id, "check_date": "10/05"})
    assert r.status_code == 400
    assert "格式错误" in r.json()["detail"]


def test_api_not_found_404s(api):
    assert api.get("/admin/warehouse/stock-checks/999999").status_code == 404
    assert api.put("/admin/warehouse/stock-checks/999999/items", json={"items": [{"item_id": 1, "actual_qty": 1}]}).status_code == 404
    assert api.post("/admin/warehouse/stock-checks/999999/complete").status_code == 404
    assert api.delete("/admin/warehouse/stock-checks/999999").status_code == 404


def test_api_delete_draft_ok(api, session, tenant, sku):
    wh = _mk_wh(session, tenant.id)
    _mk_stock(session, tenant.id, wh.id, sku.id, 10)
    r = api.post("/admin/warehouse/stock-checks", json={"warehouse_id": wh.id})
    ck_id = r.json()["data"]["id"]
    r = api.delete(f"/admin/warehouse/stock-checks/{ck_id}")
    assert r.status_code == 200
    assert api.get(f"/admin/warehouse/stock-checks/{ck_id}").status_code == 404
