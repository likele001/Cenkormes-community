from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.sku import Sku
from app.models.task import Task
from app.models.warehouse import StockLog, Warehouse
from app.models.work_order import WorkOrder


def get_work_order_by_id(db: Session, tenant_id: int, work_order_id: int, with_tasks: bool = False) -> WorkOrder | None:
    stmt = select(WorkOrder).where(WorkOrder.tenant_id == tenant_id, WorkOrder.id == work_order_id)
    if with_tasks:
        stmt = stmt.options(selectinload(WorkOrder.tasks).selectinload(Task.process))
    return db.scalar(stmt)


def list_work_orders(
    db: Session,
    tenant_id: int,
    order_id: int | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[WorkOrder]:
    stmt = (
        select(WorkOrder)
        .where(WorkOrder.tenant_id == tenant_id)
        .options(
            selectinload(WorkOrder.sku).selectinload(Sku.product),
            selectinload(WorkOrder.product),
        )
    )
    if order_id is not None:
        stmt = stmt.where(WorkOrder.order_id == order_id)
    if status:
        stmt = stmt.where(WorkOrder.status == status)
    stmt = stmt.order_by(WorkOrder.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def sum_work_order_good_qty(db: Session, tenant_id: int, work_order_id: int) -> int:
    """统一汇总一个工单的质检通过（qc_approved）良品数。

    兼容两种报工形态：
    - 批量报工 Report：sum(good_qty)，且 status='qc_approved'
    - 逐件报工 ReportUnit：count 且 status='qc_approved' 且 result_type='good'
    """
    from app.models.report import Report
    from app.models.report_unit import ReportUnit

    sub_task_ids = select(Task.id).where(Task.tenant_id == tenant_id, Task.work_order_id == work_order_id)

    batch = int(
        db.scalar(
            select(func.coalesce(func.sum(Report.good_qty), 0)).where(
                Report.tenant_id == tenant_id,
                Report.task_id.in_(sub_task_ids),
                Report.status == "qc_approved",
            )
        )
        or 0
    )
    unit = int(
        db.scalar(
            select(func.count(ReportUnit.id)).where(
                ReportUnit.tenant_id == tenant_id,
                ReportUnit.task_id.in_(sub_task_ids),
                ReportUnit.status == "qc_approved",
                ReportUnit.result_type == "good",
            )
        )
        or 0
    )
    return batch + unit


def pick_default_warehouse(db: Session, tenant_id: int) -> Warehouse | None:
    """取该租户第一个启用的仓库（与发货模块默认仓库口径一致）。"""
    return db.scalar(
        select(Warehouse)
        .where(Warehouse.tenant_id == tenant_id, Warehouse.is_active.is_(True))
        .order_by(Warehouse.id.asc())
        .limit(1)
    )


def work_order_already_stocked_in(db: Session, tenant_id: int, work_order_id: int) -> bool:
    """判断该工单是否已做过工单级生产入库（幂等）。

    判定：biz_type='produce_in' + biz_id=wo.id + remark 含“完工入库”。
    注意：件次入库（biz_id=ReportUnit.id）与工单 id 域重叠，须靠 remark 关键字区分；
    关键字与下面 stock_in_work_order 及 report_units.py 的写入文案耦合，改动需同步。
    """
    n = db.scalar(
        select(func.count(StockLog.id)).where(
            StockLog.tenant_id == tenant_id,
            StockLog.biz_type == "produce_in",
            StockLog.biz_id == work_order_id,
            StockLog.remark.like("%完工入库%"),
        )
    )
    return int(n or 0) > 0


def _unit_stocked_qty(db: Session, tenant_id: int, work_order_id: int) -> int:
    """统计该工单下件次已入库（单位报工模式）的良品数量。

    件次入库由件次终审逐件写入（biz_type='produce_in'，biz_id=ReportUnit.id，
    remark 含“件次…自动入库”），工单完工入库时须扣除，避免同一批良品重复入账。
    """
    from app.models.report_unit import ReportUnit

    sub_task_ids = select(Task.id).where(Task.tenant_id == tenant_id, Task.work_order_id == work_order_id)
    unit_ids = select(ReportUnit.id).where(
        ReportUnit.tenant_id == tenant_id, ReportUnit.task_id.in_(sub_task_ids)
    )
    qty = db.scalar(
        select(func.coalesce(func.sum(StockLog.change_qty), 0)).where(
            StockLog.tenant_id == tenant_id,
            StockLog.biz_type == "produce_in",
            StockLog.biz_id.in_(unit_ids),
            StockLog.remark.like("%件次%自动入库%"),
        )
    )
    return int(qty or 0)


def stock_in_work_order(db: Session, tenant_id: int, wo: WorkOrder) -> int | None:
    """工单完工后，将尚未入账的质检合格成品入库（成品 #sku_id 入默认仓库）。

    幂等：
    - 工单级入库已存在（biz_id=wo.id 且 remark 含“完工入库”）→ 跳过；
    - 单位报工模式下件次终审已按件入库（biz_id=unit.id），仅补入差额，避免双重入库。
    返回本次入库数量；无可入库/已有入库/无默认仓库时返回 None。
    """
    from app.crud.warehouse import adjust_stock

    if wo.tenant_id != tenant_id:
        return None
    if work_order_already_stocked_in(db, tenant_id, wo.id):
        return None

    good_qty = sum_work_order_good_qty(db, tenant_id, wo.id)
    if good_qty <= 0:
        return None

    pending_qty = good_qty - _unit_stocked_qty(db, tenant_id, wo.id)
    if pending_qty <= 0:
        return None

    wh = pick_default_warehouse(db, tenant_id)
    if not wh:
        return None

    adjust_stock(
        db,
        tenant_id=tenant_id,
        warehouse_id=wh.id,
        sku_id=wo.sku_id,
        change_qty=pending_qty,
        biz_type="produce_in",
        biz_id=wo.id,
        remark=f"工单#{wo.id} 完工入库 {pending_qty} 件",
    )
    db.flush()
    return pending_qty
