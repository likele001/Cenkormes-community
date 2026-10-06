"""外协发料护栏（P0-2）回归测试

覆盖：
- 正常发料累加 sent_qty
- 超发拒绝
- 跨租户明细拒绝（且不改动对方数据）
- 同租户其他委外单明细拒绝
- 非正数 / 重复明细拒绝
"""
from __future__ import annotations

import itertools

import pytest

from app.crud.subcontract import create_send_logs
from app.models.material import Supplier
from app.models.subcontract import SubcontractOrder, SubcontractOrderItem
from app.models.tenant import Tenant

_counter = itertools.count(1)


def _mk_order(db, tenant: Tenant, sku):
    n = next(_counter)
    sup = Supplier(tenant_id=tenant.id, code=f"S{n}", name=f"供应商{n}")
    db.add(sup)
    db.flush()
    sc = SubcontractOrder(tenant_id=tenant.id, supplier_id=sup.id, code=f"SC-{n}")
    db.add(sc)
    db.flush()
    it = SubcontractOrderItem(tenant_id=tenant.id, order_id=sc.id, sku_id=sku.id, qty=10)
    db.add(it)
    db.flush()
    return sc, it


def test_send_ok(session, tenant, sku):
    """正常发料：日志落库、sent_qty 累加。"""
    sc, it = _mk_order(session, tenant, sku)
    logs = create_send_logs(session, tenant.id, sc.id, [{"item_id": it.id, "qty": 4}], sent_by=None)
    assert len(logs) == 1
    assert it.sent_qty == 4


def test_send_over_limit_rejected(session, tenant, sku):
    """累计发料超过委外数量 → 拒绝且不落库。"""
    sc, it = _mk_order(session, tenant, sku)
    create_send_logs(session, tenant.id, sc.id, [{"item_id": it.id, "qty": 8}])
    with pytest.raises(ValueError):
        create_send_logs(session, tenant.id, sc.id, [{"item_id": it.id, "qty": 3}])
    assert it.sent_qty == 8


def test_send_cross_tenant_item_rejected(session, tenant, sku):
    """他租户明细 id → 拒绝，且不改动他租户数据。"""
    other = Tenant(code="OTHER3", name="他厂3")
    session.add(other)
    session.flush()
    _, other_item = _mk_order(session, other, sku)
    sc, _ = _mk_order(session, tenant, sku)

    with pytest.raises(ValueError):
        create_send_logs(session, tenant.id, sc.id, [{"item_id": other_item.id, "qty": 1}])
    assert (other_item.sent_qty or 0) == 0


def test_send_other_order_item_rejected(session, tenant, sku):
    """同租户但属于其他委外单的明细 → 拒绝。"""
    sc1, _ = _mk_order(session, tenant, sku)
    _, it2 = _mk_order(session, tenant, sku)
    with pytest.raises(ValueError):
        create_send_logs(session, tenant.id, sc1.id, [{"item_id": it2.id, "qty": 1}])


def test_send_non_positive_and_duplicate(session, tenant, sku):
    """非正数数量、同次重复明细 → 拒绝。"""
    sc, it = _mk_order(session, tenant, sku)
    with pytest.raises(ValueError):
        create_send_logs(session, tenant.id, sc.id, [{"item_id": it.id, "qty": 0}])
    with pytest.raises(ValueError):
        create_send_logs(
            session, tenant.id, sc.id,
            [{"item_id": it.id, "qty": 1}, {"item_id": it.id, "qty": 1}],
        )
    assert (it.sent_qty or 0) == 0
