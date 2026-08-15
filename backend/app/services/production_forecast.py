"""交期/缺料/产出简易预测"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.crud.order import get_order_by_id
from app.crud.production_plan import get_plan_by_id
from app.models.report import Report
from app.models.task import Task
from app.models.work_order import WorkOrder
from app.services.plan_readiness import build_plan_readiness


def build_plan_forecast(db: Session, tenant_id: int, plan_id: int) -> dict:
    plan = get_plan_by_id(db, tenant_id=tenant_id, plan_id=plan_id)
    if not plan:
        raise ValueError("计划不存在")
    order = get_order_by_id(db, tenant_id=tenant_id, order_id=plan.order_id, with_items=False)
    if not order:
        raise ValueError("订单不存在")

    since = datetime.utcnow() - timedelta(days=7)
    avg_daily = db.scalar(
        select(func.coalesce(func.sum(Report.good_qty), 0))
        .where(Report.tenant_id == tenant_id, Report.created_at >= since, Report.status == "qc_approved")
    )
    avg_daily = float(avg_daily or 0) / 7.0

    remaining_tasks = db.scalar(
        select(func.count(Task.id))
        .select_from(WorkOrder)
        .join(Task, and_(Task.work_order_id == WorkOrder.id, Task.tenant_id == WorkOrder.tenant_id))
        .where(WorkOrder.tenant_id == tenant_id, WorkOrder.order_id == plan.order_id, Task.status != "done")
    )
    remaining_tasks = int(remaining_tasks or 0)

    due_risk = "green"
    days_left = None
    if order.due_date:
        days_left = (order.due_date - datetime.utcnow().date()).days
        est_days = remaining_tasks * 0.5 if avg_daily <= 0 else max(1, remaining_tasks / max(avg_daily, 0.1))
        if days_left < 0:
            due_risk = "red"
        elif days_left < est_days:
            due_risk = "yellow"

    kitting_ok = True
    shortage_count = 0
    try:
        readiness = build_plan_readiness(db, tenant_id=tenant_id, order_id=plan.order_id, plan_id=plan_id)
        kitting_ok = readiness["kitting"]["ok"]
        shortage_count = readiness["kitting"]["shortage_count"]
    except ValueError:
        pass

    return {
        "plan_id": plan_id,
        "order_id": order.id,
        "due_date": order.due_date.isoformat() if order.due_date else None,
        "days_left": days_left,
        "due_risk": due_risk,
        "remaining_tasks": remaining_tasks,
        "avg_daily_output_7d": round(avg_daily, 2),
        "kitting_ok": kitting_ok,
        "shortage_count": shortage_count,
        "notes": ["统计预测，非机器学习模型"],
    }
