from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.report import Report
from app.models.task import Task


def get_dashboard_summary(db: Session, tenant_id: int, today: date | None = None) -> dict:
    if today is None:
        today = date.today()
    start_dt = datetime.combine(today, time.min)
    end_dt = start_dt + timedelta(days=1)

    row = db.execute(
        select(
            func.coalesce(func.sum(Report.good_qty), 0).label("good_qty"),
            func.coalesce(func.sum(Report.bad_qty), 0).label("bad_qty"),
            func.count(Report.id).label("report_count"),
        ).where(
            Report.tenant_id == tenant_id,
            Report.status == "qc_approved",
            Report.created_at >= start_dt,
            Report.created_at < end_dt,
        )
    ).one()
    today_good_qty = int(row.good_qty or 0)
    today_bad_qty = int(row.bad_qty or 0)
    today_total_qty = today_good_qty + today_bad_qty
    today_yield_rate = round(today_good_qty / today_total_qty, 6) if today_total_qty > 0 else None

    pending_report_count = int(
        db.scalar(
            select(func.count(Report.id)).where(
                Report.tenant_id == tenant_id,
                Report.status.in_(("submitted", "leader_approved")),
            )
        )
        or 0
    )

    orders_total = int(db.scalar(select(func.count(Order.id)).where(Order.tenant_id == tenant_id)) or 0)
    orders_confirmed = int(
        db.scalar(select(func.count(Order.id)).where(Order.tenant_id == tenant_id, Order.status == "confirmed")) or 0
    )

    tasks_total = int(db.scalar(select(func.count(Task.id)).where(Task.tenant_id == tenant_id)) or 0)
    tasks_pending = int(
        db.scalar(select(func.count(Task.id)).where(Task.tenant_id == tenant_id, Task.status == "pending")) or 0
    )
    tasks_done = int(db.scalar(select(func.count(Task.id)).where(Task.tenant_id == tenant_id, Task.status == "done")) or 0)

    return {
        "today": {
            "date": today.isoformat(),
            "good_qty": today_good_qty,
            "bad_qty": today_bad_qty,
            "total_qty": today_total_qty,
            "yield_rate": today_yield_rate,
            "report_count": int(row.report_count or 0),
        },
        "orders": {"total": orders_total, "confirmed": orders_confirmed},
        "tasks": {"total": tasks_total, "pending": tasks_pending, "done": tasks_done},
        "reports": {"pending_audit": pending_report_count},
    }


def get_dashboard_charts(db: Session, tenant_id: int, days: int = 14) -> dict:
    """首页趋势图数据：日报工趋势 + 工序排名"""
    today = date.today()
    date_from = today - timedelta(days=days - 1)

    # ── 日趋势 ──
    day_col = func.date(Report.created_at).label("day")
    trend_rows = db.execute(
        select(
            day_col,
            func.coalesce(func.sum(Report.good_qty), 0).label("good_qty"),
            func.coalesce(func.sum(Report.bad_qty), 0).label("bad_qty"),
        )
        .where(
            Report.tenant_id == tenant_id,
            Report.status == "qc_approved",
            Report.created_at >= datetime.combine(date_from, time.min),
            Report.created_at < datetime.combine(today + timedelta(days=1), time.min),
        )
        .group_by(day_col)
        .order_by(day_col.asc())
    ).all()

    by_day: dict[str, dict] = {}
    for r in trend_rows:
        d = r.day.isoformat() if isinstance(r.day, date) else str(r.day)[:10]
        g = int(r.good_qty or 0)
        b = int(r.bad_qty or 0)
        by_day[d] = {"date": d, "good_qty": g, "bad_qty": b, "total_qty": g + b}

    daily_trend: list[dict] = []
    cur = date_from
    while cur <= today:
        ds = cur.isoformat()
        daily_trend.append(by_day.get(ds) or {"date": ds, "good_qty": 0, "bad_qty": 0, "total_qty": 0})
        cur += timedelta(days=1)

    # ── 工序排名 ──
    from app.models.process import Process
    from app.models.task import Task

    rank_rows = db.execute(
        select(
            Task.process_id.label("process_id"),
            Process.name.label("process_name"),
            func.coalesce(func.sum(Report.good_qty), 0).label("good_qty"),
            func.coalesce(func.sum(Report.bad_qty), 0).label("bad_qty"),
        )
        .select_from(Report)
        .join(Task, Task.id == Report.task_id)
        .join(Process, Process.id == Task.process_id)
        .where(
            Report.tenant_id == tenant_id,
            Task.tenant_id == tenant_id,
            Process.tenant_id == tenant_id,
            Report.status == "qc_approved",
        )
        .group_by(Task.process_id, Process.name)
        .order_by(func.sum(Report.good_qty).desc())
        .limit(10)
    ).all()

    process_rank = [
        {
            "process_id": int(r.process_id),
            "process_name": r.process_name,
            "good_qty": int(r.good_qty or 0),
            "bad_qty": int(r.bad_qty or 0),
        }
        for r in rank_rows
    ]

    return {"daily_trend": daily_trend, "process_rank": process_rank}


def get_employee_dashboard_summary(db: Session, tenant_id: int, user_id: int, today: date | None = None) -> dict:
    """H5 员工个人首页仪表盘数据（仅当前用户）"""
    if today is None:
        today = date.today()
    start_dt = datetime.combine(today, time.min)
    end_dt = start_dt + timedelta(days=1)

    today_row = db.execute(
        select(
            func.coalesce(func.sum(Report.good_qty), 0).label("good_qty"),
            func.coalesce(func.sum(Report.bad_qty), 0).label("bad_qty"),
        ).where(
            Report.tenant_id == tenant_id,
            Report.report_user_id == user_id,
            Report.created_at >= start_dt,
            Report.created_at < end_dt,
        )
    ).one()
    today_good = int(today_row.good_qty or 0)
    today_bad = int(today_row.bad_qty or 0)
    today_total = today_good + today_bad
    today_yield = round(today_good / today_total, 6) if today_total > 0 else None


    from app.models.task_assignment import TaskAssignment

    def _count_my_tasks(task_status: str) -> int:
        return int(
            db.scalar(
                select(func.count(func.distinct(Task.id)))
                .select_from(Task)
                .join(
                    TaskAssignment,
                    (TaskAssignment.task_id == Task.id) & (TaskAssignment.tenant_id == Task.tenant_id),
                )
                .where(
                    Task.tenant_id == tenant_id,
                    TaskAssignment.user_id == user_id,
                    Task.status == task_status,
                )
            )
            or 0
        )

    my_pending_tasks = _count_my_tasks("pending")
    my_working_tasks = _count_my_tasks("working")

    month_start = date(today.year, today.month, 1)

    # 本月报工总数
    month_report_count = int(
        db.scalar(
            select(func.count(Report.id)).where(
                Report.tenant_id == tenant_id,
                Report.report_user_id == user_id,
                Report.created_at >= datetime.combine(month_start, time.min),
                Report.created_at < end_dt,
            )
        )
        or 0
    )

    return {
        "today": {
            "date": today.isoformat(),
            "good_qty": today_good,
            "bad_qty": today_bad,
            "total_qty": today_total,
            "yield_rate": today_yield,
        },
        "my_tasks": {
            "pending": my_pending_tasks,
            "working": my_working_tasks,
            "total": my_pending_tasks + my_working_tasks,
        },
        "month": {
            "month": today.strftime("%Y-%m"),
            "report_count": month_report_count,
        },
    }
