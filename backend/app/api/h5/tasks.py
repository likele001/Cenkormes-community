from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import ok
from app.crud.dashboard import get_employee_dashboard_summary
from app.crud.notification import create_notification
from app.crud.report import create_report
from app.crud.task import get_task_by_id, get_task_by_code
from app.crud.task_assignment import (
    get_assignment,
    sum_user_reported_qty,
    validate_report_qty_limit,
)
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.tenant import Tenant
from app.models.user import User
from app.services.task_qr import task_qr_payload


router = APIRouter()


def _ensure_employee(user: User) -> None:
    roles = {r.code for r in user.roles}
    if not ({"employee", "leader"} & roles):
        raise HTTPException(status_code=403, detail="无权限")


def _my_assignment_fields(db: Session, tenant_id: int, task: Task, user_id: int) -> dict:
    a = get_assignment(db, tenant_id, task.id, user_id)
    if not a:
        return {
            "assigned_qty": 0,
            "reported_qty": 0,
            "remaining_qty": 0,
            "use_unit_report": False,
            "report_mode": "batch",
        }
    reported = sum_user_reported_qty(db, tenant_id, task.id, user_id)
    return {
        "assigned_qty": int(a.assigned_qty),
        "reported_qty": reported,
        "remaining_qty": max(0, int(a.assigned_qty) - reported),
        "use_unit_report": False,
        "report_mode": "batch",
    }


def _task_out(x, db: Session, tenant_id: int, user_id: int) -> dict:
    wo = x.work_order
    sku = wo.sku if wo else None
    order = wo.order if wo and getattr(wo, "order", None) else None
    extra = _my_assignment_fields(db, tenant_id, x, user_id)
    assigned = int(extra.get("assigned_qty") or 0)
    reported = int(extra.get("reported_qty") or 0)
    progress_pct = round(reported / assigned * 100) if assigned > 0 else 0
    return {
        "id": x.id,
        "tenant_id": x.tenant_id,
        "task_code": x.task_code,
        "work_order_id": x.work_order_id,
        "process_id": x.process_id,
        "seq": x.seq,
        "planned_qty": x.planned_qty,
        "status": x.status,
        "assigned_user_id": x.assigned_user_id,
        "assigned_at": x.assigned_at,
        "assigned_by": x.assigned_by,
        **extra,
        "progress_pct": progress_pct,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "process": {"id": x.process.id, "code": x.process.code, "name": x.process.name} if x.process else None,
        "work_order": (
            {
                "id": wo.id,
                "order_id": wo.order_id,
                "order_code": order.code if order else None,
                "qty": wo.qty,
                "sku": (
                    {
                        "id": sku.id,
                        "code": sku.code,
                        "name": sku.name,
                        "color": sku.color,
                        "spec": sku.spec,
                        "display_label": f"{sku.code} - {sku.name}" if sku.name else sku.code,
                    }
                    if sku
                    else None
                ),
            }
            if wo
            else None
        ),
    }


@router.get("/tasks")
def my_tasks_api(
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_employee(user)
    stmt = (
        select(Task)
        .join(TaskAssignment, (TaskAssignment.task_id == Task.id) & (TaskAssignment.tenant_id == Task.tenant_id))
        .where(
            Task.tenant_id == user.tenant_id,
            TaskAssignment.user_id == user.id,
        )
    )
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.id.desc()).offset(offset).limit(limit)
    from sqlalchemy.orm import selectinload
    from app.models.work_order import WorkOrder

    stmt = stmt.options(
        selectinload(Task.process),
        selectinload(Task.work_order).selectinload(WorkOrder.sku),
        selectinload(Task.work_order).selectinload(WorkOrder.order),
    )
    items = db.scalars(stmt).all()
    return ok({"items": [_task_out(x, db, user.tenant_id, user.id) for x in items]})


@router.get("/tasks/{task_code}")
def my_task_detail_api(
    task_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_employee(user)
    if task_code.isdigit():
        item = get_task_by_id(db, tenant_id=user.tenant_id, task_id=int(task_code), with_refs=True)
    else:
        item = get_task_by_code(db, tenant_id=user.tenant_id, task_code=task_code, with_refs=True)
    if not item:
        raise HTTPException(status_code=400, detail="任务不存在")
    if not get_assignment(db, user.tenant_id, item.id, user.id):
        raise HTTPException(status_code=403, detail="无权限")
    return ok(_task_out(item, db, user.tenant_id, user.id))


@router.get("/tasks/{task_code}/qr")
def my_task_qr_api(
    task_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """员工查看本人任务的报工二维码（派工后在此扫码报工）。"""
    _ensure_employee(user)
    if task_code.isdigit():
        item = get_task_by_id(db, tenant_id=user.tenant_id, task_id=int(task_code), with_refs=False)
    else:
        item = get_task_by_code(db, tenant_id=user.tenant_id, task_code=task_code, with_refs=False)
    if not item:
        raise HTTPException(status_code=400, detail="任务不存在")
    if not get_assignment(db, user.tenant_id, item.id, user.id):
        raise HTTPException(status_code=403, detail="无权限")
    tenant = db.get(Tenant, user.tenant_id)
    tc = tenant.code if tenant else None
    return ok(task_qr_payload(item.task_code, tc))


# ── 报工 ──

@router.post("/reports")
def submit_report_api(
    task_code: str = Query(min_length=1),
    good_qty: int = Query(ge=0),
    bad_qty: int = Query(default=0, ge=0),
    remark: str | None = Query(default=None, max_length=500),
    attachment_ids: str | None = Query(default=None, max_length=512),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_employee(user)
    task = get_task_by_code(db, tenant_id=user.tenant_id, task_code=task_code, with_refs=False)
    if not task:
        raise HTTPException(status_code=400, detail="任务不存在")
    assignment = get_assignment(db, user.tenant_id, task.id, user.id)
    if not assignment:
        raise HTTPException(status_code=403, detail="您未被派工到此任务")
    if task.status == "done":
        raise HTTPException(status_code=400, detail="任务已完成")
    if good_qty + bad_qty <= 0:
        raise HTTPException(status_code=400, detail="合格数+不良数必须大于0")
    try:
        validate_report_qty_limit(
            db,
            tenant_id=user.tenant_id,
            task=task,
            user_id=user.id,
            good_qty=good_qty,
            bad_qty=bad_qty,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    report = create_report(
        db,
        tenant_id=user.tenant_id,
        task_id=task.id,
        report_user_id=user.id,
        good_qty=good_qty,
        bad_qty=bad_qty,
        remark=remark,
        attachment_ids=attachment_ids,
    )
    create_notification(
        db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        title="报工已提交",
        content=f"任务 {task_code} 报工已提交：合格 {good_qty}，不良 {bad_qty}",
        level="info",
        biz_type="report",
        biz_id=report.id,
    )
    db.commit()

    return ok({
        "id": report.id,
        "status": report.status,
        "good_qty": report.good_qty,
        "bad_qty": report.bad_qty,
        "created_at": report.created_at,
    })


@router.get("/reports")
def my_reports_api(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_employee(user)
    from app.crud.report import list_reports
    items = list_reports(db, tenant_id=user.tenant_id, report_user_id=user.id, offset=offset, limit=limit)
    return ok({
        "items": [
            {
                "id": r.id,
                "task_id": r.task_id,
                "good_qty": r.good_qty,
                "bad_qty": r.bad_qty,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in items
        ]
    })



# ── 首页仪表盘 ──

@router.get("/dashboard/summary")
def my_dashboard_summary_api(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """员工个人首页仪表盘"""
    data = get_employee_dashboard_summary(db, tenant_id=user.tenant_id, user_id=user.id)
    return ok(data)
