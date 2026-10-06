from io import BytesIO

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.crud.task import get_task_by_id, list_tasks
from app.crud.task_assignment import (
    list_assignments_for_task,
    replace_task_assignments,
    sum_assigned_qty,
    sum_user_reported_qty,
)
from app.models.tenant import Tenant
from app.services.task_qr import task_qr_payload
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskAssignIn, TaskAssignmentsIn, TaskLabelBatchIn
from app.services.dispatch_candidates import list_dispatch_candidate_users
from app.services.entity_refs import process_ref_dict, product_ref_dict, sku_ref_dict


router = APIRouter(dependencies=[Depends(require_permissions(["task.manage"]))])


def _assignment_out(a) -> dict:
    u = getattr(a, "user", None)
    return {
        "id": a.id,
        "user_id": a.user_id,
        "assigned_qty": a.assigned_qty,
        "reported_qty": getattr(a, "_reported_qty", None),
        "remaining_qty": getattr(a, "_remaining_qty", None),
        "assigned_at": a.assigned_at,
        "assigned_by": a.assigned_by,
        "user": {"id": u.id, "username": u.username, "full_name": u.full_name} if u else None,
    }


def _out(x, db: Session | None = None, tenant_id: int | None = None) -> dict:
    assignments = []
    assigned_total = 0
    if db is not None and tenant_id is not None:
        rows = list_assignments_for_task(db, tenant_id=tenant_id, task_id=x.id)
        assigned_total = sum(int(r.assigned_qty) for r in rows)
        for r in rows:
            reported = sum_user_reported_qty(db, tenant_id, x.id, r.user_id)
            r._reported_qty = reported  # noqa: SLF001
            r._remaining_qty = max(0, int(r.assigned_qty) - reported)
            assignments.append(_assignment_out(r))
    wo = getattr(x, "work_order", None)
    order = wo.order if wo and getattr(wo, "order", None) else None
    customer = order.customer if order and getattr(order, "customer", None) else None
    sku = wo.sku if wo else None
    product = (wo.product if wo and getattr(wo, "product", None) else None) or (
        sku.product if sku and getattr(sku, "product", None) else None
    )
    sku_out = sku_ref_dict(sku, product)
    return {
        "id": x.id,
        "tenant_id": x.tenant_id,
        "work_order_id": x.work_order_id,
        "process_id": x.process_id,
        "seq": x.seq,
        "task_code": x.task_code,
        "planned_qty": x.planned_qty,
        "status": x.status,
        "assigned_user_id": x.assigned_user_id,
        "assigned_at": x.assigned_at,
        "assigned_by": x.assigned_by,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "process": process_ref_dict(getattr(x, "process", None)),
        "assignments": assignments,
        "assigned_total_qty": assigned_total,
        "unassigned_qty": max(0, int(x.planned_qty) - assigned_total),
        "order": (
            {
                "id": order.id,
                "code": order.code,
                "status": order.status,
                "customer_id": order.customer_id,
                "customer_name": customer.name if customer else None,
                "customer_code": customer.code if customer else None,
            }
            if order
            else None
        ),
        "sku": sku_out,
        "product": product_ref_dict(product),
        "work_order": (
            {
                "id": wo.id,
                "order_id": wo.order_id,
                "sku_id": wo.sku_id,
                "qty": wo.qty,
                "sku_display_label": sku_out.get("display_label") if sku_out else None,
            }
            if wo
            else None
        ),
    }


def _tenant_code(db: Session, tenant_id: int) -> str | None:
    t = db.get(Tenant, tenant_id)
    return t.code if t else None


def _extract_head_body(html: str) -> tuple[str, str] | None:
    m_head = re.search(r"<head[^>]*>([\s\S]*?)</head>", html, flags=re.I)
    m_body = re.search(r"<body[^>]*>([\s\S]*?)</body>", html, flags=re.I)
    if not m_head or not m_body:
        return None
    return (m_head.group(1), m_body.group(1))


@router.get("")
def list_api(
    work_order_id: int | None = Query(default=None, ge=1),
    assigned_user_id: int | None = Query(default=None, ge=1),
    keyword: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = list_tasks(
        db,
        tenant_id=user.tenant_id,
        work_order_id=work_order_id,
        assigned_user_id=assigned_user_id,
        keyword=keyword,
        status=status,
        with_refs=True,
        offset=offset,
        limit=limit,
    )
    return ok({"items": [_out(x, db=db, tenant_id=user.tenant_id) for x in items]})


@router.get("/dispatch-users", dependencies=[Depends(require_permissions(["dispatch.manage"]))])
def list_dispatch_users_api(
    keyword: str | None = Query(default=None, max_length=50),
    skill_ids: str | None = Query(default=None, max_length=200, description="逗号分隔技能ID，例如 1,2,3"),
    match: str = Query(default="all", max_length=8, description="all/any"),
    include_leader: bool = Query(default=False),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ids: list[int] = []
    if skill_ids:
        for part in skill_ids.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        ids = [x for x in ids if x > 0]
        ids = list(dict.fromkeys(ids))

    if match not in {"all", "any"}:
        raise HTTPException(status_code=400, detail="match 参数必须为 all 或 any")

    items = list_dispatch_candidate_users(
        db,
        user.tenant_id,
        include_leader=include_leader,
        skill_ids=ids or None,
        skill_match=match,
        keyword=keyword,
        offset=offset,
        limit=limit,
    )
    return ok({"items": [{"id": u.id, "username": u.username, "full_name": u.full_name} for u in items]})


@router.put("/{task_id}/assignments", dependencies=[Depends(require_permissions(["dispatch.manage"]))])
def set_assignments_api(
    task_id: int,
    payload: TaskAssignmentsIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = get_task_by_id(db, tenant_id=user.tenant_id, task_id=task_id, with_refs=False)
    if not task:
        raise HTTPException(status_code=400, detail="任务不存在")
    items = [{"user_id": x.user_id, "assigned_qty": x.assigned_qty} for x in payload.items]
    if items:
        from app.crud.task_assignment import ensure_users_exist

        try:
            ensure_users_exist(db, user.tenant_id, [x["user_id"] for x in items])
            replace_task_assignments(
                db,
                tenant_id=user.tenant_id,
                task=task,
                items=items,
                dispatcher_user_id=user.id,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        replace_task_assignments(db, tenant_id=user.tenant_id, task=task, items=[], dispatcher_user_id=user.id)
    db.commit()
    item = get_task_by_id(db, tenant_id=user.tenant_id, task_id=task.id, with_refs=True)
    if not item:
        raise HTTPException(status_code=500, detail="派工失败")
    return ok(_out(item, db=db, tenant_id=user.tenant_id))


@router.post("/{task_id}/assign", dependencies=[Depends(require_permissions(["dispatch.manage"]))])
def assign_api(
    task_id: int,
    payload: TaskAssignIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """兼容旧接口：单人派工时分配全部计划数量。"""
    task = get_task_by_id(db, tenant_id=user.tenant_id, task_id=task_id, with_refs=False)
    if not task:
        raise HTTPException(status_code=400, detail="任务不存在")
    items: list[dict] = []
    if payload.assigned_user_id is not None:
        items = [{"user_id": payload.assigned_user_id, "assigned_qty": int(task.planned_qty)}]
    body = TaskAssignmentsIn(items=items)
    return set_assignments_api(task_id=task_id, payload=body, db=db, user=user)


@router.get("/{task_id}")
def get_api(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = get_task_by_id(db, tenant_id=user.tenant_id, task_id=task_id, with_refs=True)
    if not item:
        raise HTTPException(status_code=400, detail="任务不存在")
    return ok(_out(item, db=db, tenant_id=user.tenant_id))
