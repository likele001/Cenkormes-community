"""双重入库去重（P0-4）回归测试

背景：单位报工模式下件次终审按件入库（biz_id=ReportUnit.id），
工单完工又按 sum_work_order_good_qty 全量入库（biz_id=WorkOrder.id），
两表 id 域独立重叠，仅凭 biz_id 无法区分，导致同一批良品重复入账。

覆盖：
- 单位报工：件次全部已入库 → 工单完工不再入库
- 批量报工：工单完工全量入库且幂等
- 混合模式：件次已入库 + 批量报工 → 只补差额
- id 碰撞：件次日志 biz_id 与工单 id 相同 → 不误判“工单已入库”
- 件次未入库（如当时无仓库）→ 工单完工按差额补全
- 无默认仓库 → 返回 None
"""
from __future__ import annotations

from sqlalchemy import select

from app.crud.warehouse import adjust_stock, get_stock
from app.crud.work_order import stock_in_work_order, sum_work_order_good_qty
from app.models.order import Order, OrderItem
from app.models.report import Report
from app.models.report_unit import ReportUnit
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.warehouse import StockLog, Warehouse
from app.models.work_order import WorkOrder


def _mk_wo_task(session, tenant, customer, sku, process, suffix: str, qty: int = 10, wo_id: int | None = None):
    o = Order(tenant_id=tenant.id, customer_id=customer.id, code=f"ORD-DBL-{suffix}", status="confirmed")
    session.add(o)
    session.flush()
    oi = OrderItem(tenant_id=tenant.id, order_id=o.id, line_no=1, sku_id=sku.id, qty=qty)
    session.add(oi)
    session.flush()
    wo = WorkOrder(
        tenant_id=tenant.id, order_id=o.id, order_item_id=oi.id,
        product_id=sku.product_id, sku_id=sku.id, qty=qty, status="done",
    )
    if wo_id is not None:
        wo.id = wo_id  # 显式指定，模拟两表 id 域重叠
    session.add(wo)
    session.flush()
    task = Task(
        tenant_id=tenant.id, work_order_id=wo.id, process_id=process.id, seq=1,
        task_code=f"TK-DBL-{suffix}", planned_qty=qty, status="done",
    )
    session.add(task)
    session.flush()
    return wo, task


def _mk_warehouse(session, tenant, code: str = "WH1") -> Warehouse:
    wh = Warehouse(tenant_id=tenant.id, code=code, name=code)
    session.add(wh)
    session.flush()
    return wh


def _mk_unit(session, tenant, task, user, seq: int, unit_id: int | None = None) -> ReportUnit:
    ta = session.scalar(
        select(TaskAssignment).where(
            TaskAssignment.tenant_id == tenant.id,
            TaskAssignment.task_id == task.id,
            TaskAssignment.user_id == user.id,
        )
    )
    if ta is None:
        ta = TaskAssignment(tenant_id=tenant.id, task_id=task.id, user_id=user.id, assigned_qty=1)
        session.add(ta)
        session.flush()
    unit = ReportUnit(
        tenant_id=tenant.id, task_assignment_id=ta.id, task_id=task.id,
        user_id=user.id, unit_seq=seq, result_type="good", status="qc_approved",
    )
    if unit_id is not None:
        unit.id = unit_id  # 显式指定，模拟与工单 id 碰撞
    session.add(unit)
    session.flush()
    return unit


def _unit_stock_in(session, tenant, wh, wo, unit) -> None:
    """模拟件次终审自动入库（remark 文案与 report_units.py 写入保持一致）。"""
    adjust_stock(
        session, tenant.id, wh.id, wo.sku_id, 1, "produce_in",
        biz_id=unit.id, remark=f"工单#{wo.id} 件次#{unit.unit_seq} 终审通过自动入库",
    )


def _mk_batch_report(session, tenant, task, user, good_qty: int) -> Report:
    r = Report(
        tenant_id=tenant.id, task_id=task.id, report_user_id=user.id,
        good_qty=good_qty, bad_qty=0, status="qc_approved",
    )
    session.add(r)
    session.flush()
    return r


def _wo_stock_logs(session, tenant, wo) -> list[StockLog]:
    return session.scalars(
        select(StockLog).where(
            StockLog.tenant_id == tenant.id,
            StockLog.biz_type == "produce_in",
            StockLog.biz_id == wo.id,
            StockLog.remark.like("%完工入库%"),
        )
    ).all()


def test_unit_mode_all_stocked_skips(session, tenant, test_user, customer, sku, process):
    """单位报工：3 件全部按件入库 → 工单完工不重复入库。"""
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "U1")
    wh = _mk_warehouse(session, tenant)
    for seq in (1, 2, 3):
        unit = _mk_unit(session, tenant, task, test_user, seq)
        _unit_stock_in(session, tenant, wh, wo, unit)

    assert sum_work_order_good_qty(session, tenant.id, wo.id) == 3
    assert stock_in_work_order(session, tenant.id, wo) is None
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 3
    assert _wo_stock_logs(session, tenant, wo) == []


def test_batch_mode_full_stockin_idempotent(session, tenant, test_user, customer, sku, process):
    """批量报工：工单完工全量入库；重复触发幂等跳过。"""
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "B1")
    wh = _mk_warehouse(session, tenant)
    _mk_batch_report(session, tenant, task, test_user, 5)

    assert stock_in_work_order(session, tenant.id, wo) == 5
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5

    assert stock_in_work_order(session, tenant.id, wo) is None
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5
    assert len(_wo_stock_logs(session, tenant, wo)) == 1


def test_mixed_unit_and_batch_stocks_only_pending(session, tenant, test_user, customer, sku, process):
    """混合：2 件已按件入库 + 3 件批量 → 工单完工只补 3 件。"""
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "M1")
    wh = _mk_warehouse(session, tenant)
    for seq in (1, 2):
        unit = _mk_unit(session, tenant, task, test_user, seq)
        _unit_stock_in(session, tenant, wh, wo, unit)
    _mk_batch_report(session, tenant, task, test_user, 3)

    assert sum_work_order_good_qty(session, tenant.id, wo.id) == 5
    assert stock_in_work_order(session, tenant.id, wo) == 3
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5

    assert stock_in_work_order(session, tenant.id, wo) is None
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5


def test_unit_log_same_biz_id_not_false_positive(session, tenant, test_user, customer, sku, process):
    """id 碰撞：件次日志 biz_id 与工单 id 相同 → 不得误判“工单已入库”。"""
    collide = 990001
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "C1", wo_id=collide)
    wh = _mk_warehouse(session, tenant)
    unit = _mk_unit(session, tenant, task, test_user, 1, unit_id=collide)
    _unit_stock_in(session, tenant, wh, wo, unit)  # 日志 biz_id=990001 == wo.id
    _mk_batch_report(session, tenant, task, test_user, 4)

    # 1 件已按件入库 + 4 件批量待入账 → 只补 4 件
    assert sum_work_order_good_qty(session, tenant.id, wo.id) == 5
    assert stock_in_work_order(session, tenant.id, wo) == 4
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5


def test_units_not_stocked_fallback_full(session, tenant, test_user, customer, sku, process):
    """件次因无仓库等原因未入库 → 工单完工按差额补全（不丢库存）。"""
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "F1")
    wh = _mk_warehouse(session, tenant)
    for seq in (1, 2):
        _mk_unit(session, tenant, task, test_user, seq)  # 不入库
    _mk_batch_report(session, tenant, task, test_user, 3)

    assert stock_in_work_order(session, tenant.id, wo) == 5
    assert get_stock(session, tenant.id, wh.id, sku.id).qty == 5


def test_no_default_warehouse_returns_none(session, tenant, test_user, customer, sku, process):
    """无启用仓库 → 返回 None，不产生任何日志。"""
    wo, task = _mk_wo_task(session, tenant, customer, sku, process, "N1")
    _mk_batch_report(session, tenant, task, test_user, 2)

    assert stock_in_work_order(session, tenant.id, wo) is None
