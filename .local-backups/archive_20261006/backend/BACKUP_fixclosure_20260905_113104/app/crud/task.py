from datetime import datetime

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.order import Order
from app.models.process import Process
from app.models.sku import Sku
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.user import User
from app.models.work_order import WorkOrder


def _task_load_options():
    return (
        selectinload(Task.process),
        selectinload(Task.work_order).selectinload(WorkOrder.sku).selectinload(Sku.product),
        selectinload(Task.work_order).selectinload(WorkOrder.product),
        selectinload(Task.work_order).selectinload(WorkOrder.order).selectinload(Order.customer),
        selectinload(Task.equipment),
    )


def get_task_by_id(db: Session, tenant_id: int, task_id: int, with_refs: bool = False) -> Task | None:
    stmt = select(Task).where(Task.tenant_id == tenant_id, Task.id == task_id)
    if with_refs:
        stmt = stmt.options(*_task_load_options())
    return db.scalar(stmt)


def get_task_by_code(db: Session, tenant_id: int, task_code: str, with_refs: bool = False) -> Task | None:
    stmt = select(Task).where(Task.tenant_id == tenant_id, Task.task_code == task_code)
    if with_refs:
        stmt = stmt.options(*_task_load_options())
    return db.scalar(stmt)


def list_tasks(
    db: Session,
    tenant_id: int,
    work_order_id: int | None = None,
    assigned_user_id: int | None = None,
    keyword: str | None = None,
    status: str | None = None,
    with_refs: bool = False,
    offset: int = 0,
    limit: int = 50,
) -> list[Task]:
    stmt = select(Task).where(Task.tenant_id == tenant_id)
    if with_refs:
        stmt = stmt.options(*_task_load_options())
    if work_order_id is not None:
        stmt = stmt.where(Task.work_order_id == work_order_id)
    if assigned_user_id is not None:
        stmt = stmt.where(
            exists().where(
                TaskAssignment.tenant_id == Task.tenant_id,
                TaskAssignment.task_id == Task.id,
                TaskAssignment.user_id == assigned_user_id,
            )
        )
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        stmt = (
            stmt.join(WorkOrder, WorkOrder.id == Task.work_order_id)
            .join(Order, Order.id == WorkOrder.order_id)
            .outerjoin(Customer, Customer.id == Order.customer_id)
            .outerjoin(Sku, Sku.id == WorkOrder.sku_id)
            .outerjoin(Process, Process.id == Task.process_id)
            .outerjoin(
                TaskAssignment,
                (TaskAssignment.task_id == Task.id) & (TaskAssignment.tenant_id == Task.tenant_id),
            )
            .outerjoin(User, User.id == TaskAssignment.user_id)
            .where(
                or_(
                    Task.task_code.like(kw),
                    Order.code.like(kw),
                    Customer.name.like(kw),
                    Customer.code.like(kw),
                    Sku.code.like(kw),
                    Sku.name.like(kw),
                    Process.name.like(kw),
                    Process.code.like(kw),
                    User.username.like(kw),
                    User.full_name.like(kw),
                )
            )
            .distinct()
        )
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def assign_task(db: Session, task: Task, assigned_user_id: int | None, dispatcher_user_id: int) -> Task:
    task.assigned_user_id = assigned_user_id
    if assigned_user_id is None:
        task.assigned_at = None
        task.assigned_by = None
    else:
        task.assigned_at = datetime.now()
        task.assigned_by = dispatcher_user_id
    db.flush()
    return task


def set_task_equipment(db: Session, task: Task, equipment_id: int | None) -> Task:
    task.equipment_id = equipment_id
    db.flush()
    return task


def sync_task_progress(db: Session, tenant_id: int, task: Task) -> None:
    """终审通过后推进任务/工单/订单状态：任务累计合格数达标 → 任务完成 → 工单完成 → 订单完成。"""
    from app.models.report import Report
    from app.models.report_unit import ReportUnit

    batch_done = int(
        db.scalar(
            select(func.coalesce(func.sum(Report.good_qty), 0)).where(
                Report.task_id == task.id,
                Report.status == "qc_approved",
            )
        )
        or 0
    )
    unit_done = int(
        db.scalar(
            select(func.count(ReportUnit.id)).where(
                ReportUnit.task_id == task.id,
                ReportUnit.status == "qc_approved",
                ReportUnit.result_type == "good",
            )
        )
        or 0
    )
    done_qty = batch_done + unit_done

    if (task.planned_qty or 0) > 0 and done_qty >= task.planned_qty:
        task.status = "done"
    elif done_qty > 0 and task.status == "pending":
        task.status = "in_progress"
    db.flush()

    sync_work_order_progress(db, tenant_id, db.get(WorkOrder, task.work_order_id))


def sync_work_order_progress(db: Session, tenant_id: int, wo: WorkOrder | None) -> None:
    """所有任务完成 → 工单完成；有任务在制 → 工单进入进行中。"""
    if not wo or wo.tenant_id != tenant_id:
        return
    tasks = db.scalars(
        select(Task).where(Task.tenant_id == tenant_id, Task.work_order_id == wo.id)
    ).all()
    if not tasks:
        return
    if all(t.status == "done" for t in tasks):
        if wo.status != "done":
            wo.status = "done"
            wo.finished_at = datetime.now()
    elif any(t.status in ("in_progress", "done") for t in tasks):
        if wo.status == "open":
            wo.status = "in_progress"
            wo.started_at = wo.started_at or datetime.now()
    db.flush()

    sync_order_progress(db, tenant_id, db.get(Order, wo.order_id))


def sync_order_progress(db: Session, tenant_id: int, order: Order | None) -> None:
    """所有工单完成 → 订单完成。"""
    if not order or order.tenant_id != tenant_id or order.status in ("cancelled", "completed"):
        return
    wos = db.scalars(
        select(WorkOrder).where(WorkOrder.tenant_id == tenant_id, WorkOrder.order_id == order.id)
    ).all()
    if not wos:
        return
    if all(w.status == "done" for w in wos):
        order.status = "completed"
        order.actual_completed_at = datetime.now()
    elif any(w.status == "in_progress" for w in wos):
        order.status = "producing"
    db.flush()
