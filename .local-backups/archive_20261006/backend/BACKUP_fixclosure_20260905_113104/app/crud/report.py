from datetime import datetime

from sqlalchemy import select, update as sa_update
from sqlalchemy.orm import Session, selectinload

from app.models.process_price import ProcessPrice
from app.models.report import Report, ReportAudit
from app.models.salary import SalaryItem
from app.models.task import Task
from app.models.work_order import WorkOrder


# ── 报工 ──

def create_report(
    db: Session,
    tenant_id: int,
    task_id: int,
    report_user_id: int,
    good_qty: int,
    bad_qty: int,
    remark: str | None,
    attachment_ids: str | None,
) -> Report:
    report = Report(
        tenant_id=tenant_id,
        task_id=task_id,
        report_user_id=report_user_id,
        good_qty=good_qty,
        bad_qty=bad_qty,
        remark=remark,
        attachment_ids=attachment_ids,
        status="submitted",
    )
    db.add(report)
    db.flush()
    return report


def get_report_by_id(db: Session, tenant_id: int, report_id: int, *, for_update: bool = False) -> Report | None:
    stmt = (
        select(Report)
        .where(Report.tenant_id == tenant_id, Report.id == report_id)
        .options(selectinload(Report.task), selectinload(Report.audits), selectinload(Report.report_user))
    )
    if for_update:
        stmt = stmt.with_for_update()
    return db.scalar(stmt)


PENDING_AUDIT_REPORT_STATUSES = ("submitted", "leader_approved")


def list_reports(
    db: Session,
    tenant_id: int,
    task_id: int | None = None,
    report_user_id: int | None = None,
    status: str | None = None,
    pending_audit: bool = False,
    offset: int = 0,
    limit: int = 50,
) -> list[Report]:
    stmt = (
        select(Report)
        .where(Report.tenant_id == tenant_id)
        .options(selectinload(Report.report_user), selectinload(Report.task))
    )
    if task_id is not None:
        stmt = stmt.where(Report.task_id == task_id)
    if report_user_id is not None:
        stmt = stmt.where(Report.report_user_id == report_user_id)
    if pending_audit:
        stmt = stmt.where(Report.status.in_(PENDING_AUDIT_REPORT_STATUSES))
    elif status:
        stmt = stmt.where(Report.status == status)
    stmt = stmt.order_by(Report.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


# ── 审核 ──

def create_audit(
    db: Session,
    tenant_id: int,
    report_id: int,
    auditor_id: int,
    audit_level: str,
    action: str,
    reason: str | None,
) -> ReportAudit:
    audit = ReportAudit(
        tenant_id=tenant_id,
        report_id=report_id,
        auditor_id=auditor_id,
        audit_level=audit_level,
        action=action,
        reason=reason,
    )
    db.add(audit)
    db.flush()
    return audit


def update_report_status(db: Session, report: Report, new_status: str) -> Report:
    report.status = new_status
    db.flush()
    return report


# ── 工资 ──

def calc_and_create_salary(
    db: Session,
    tenant_id: int,
    report: Report,
) -> SalaryItem | None:
    """审核通过后调用，生成工资明细"""
    task = db.get(Task, report.task_id)
    if not task:
        return None

    # 查工价
    wo = db.get(WorkOrder, task.work_order_id)
    if not wo:
        return None

    price = db.scalar(
        select(ProcessPrice).where(
            ProcessPrice.tenant_id == tenant_id,
            ProcessPrice.sku_id == wo.sku_id,
            ProcessPrice.process_id == task.process_id,
            ProcessPrice.is_active.is_(True),
        )
    )
    if not price:
        # 无工价配置：通知管理员，避免员工报工通过却无工资且无人知晓
        try:
            from app.crud.notification import notify_superusers
            notify_superusers(
                db,
                tenant_id=tenant_id,
                title="报工缺工价",
                content=f"报工单 #{report.id} 终审通过但未找到工价（型号/工序），员工 {report.report_user_id} 无工资记录，请尽快配置工价",
                level="warning",
                biz_type="report",
                biz_id=report.id,
            )
        except Exception:
            pass
        return None

    from decimal import Decimal
    unit_price = Decimal(str(price.unit_price))
    amount = Decimal(str(report.good_qty)) * unit_price
    # 归属月份以报工提交时间为准，避免跨月审核导致工资记入错误月份
    month = (report.created_at or datetime.now()).strftime("%Y-%m")

    # upsert：已存在（并发/重算）则更新单价与金额，避免重复计薪
    existing = db.scalar(
        select(SalaryItem).where(
            SalaryItem.tenant_id == tenant_id,
            SalaryItem.report_id == report.id,
        )
    )
    if existing:
        existing.unit_price = unit_price
        existing.good_qty = report.good_qty
        existing.amount = amount
        existing.month = month
        db.flush()
        return existing

    item = SalaryItem(
        tenant_id=tenant_id,
        report_id=report.id,
        user_id=report.report_user_id,
        sku_id=wo.sku_id,
        process_id=task.process_id,
        unit_price=unit_price,
        good_qty=report.good_qty,
        amount=amount,
        month=month,
    )
    db.add(item)
    db.flush()
    return item


def get_salary_items(
    db: Session,
    tenant_id: int,
    user_id: int | None = None,
    month: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[SalaryItem]:
    stmt = select(SalaryItem).where(SalaryItem.tenant_id == tenant_id)
    if user_id is not None:
        stmt = stmt.where(SalaryItem.user_id == user_id)
    if month:
        stmt = stmt.where(SalaryItem.month == month)
    stmt = stmt.order_by(SalaryItem.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def get_salary_summary(
    db: Session,
    tenant_id: int,
    month: str | None = None,
    user_id: int | None = None,
) -> list[dict]:
    """按月/人汇总"""
    from sqlalchemy import func as sa_func

    stmt = (
        select(
            SalaryItem.user_id,
            SalaryItem.month,
            sa_func.sum(SalaryItem.amount).label("total_amount"),
            sa_func.sum(SalaryItem.good_qty).label("total_qty"),
        )
        .where(SalaryItem.tenant_id == tenant_id)
    )
    if month:
        stmt = stmt.where(SalaryItem.month == month)
    if user_id is not None:
        stmt = stmt.where(SalaryItem.user_id == user_id)
    stmt = stmt.group_by(SalaryItem.user_id, SalaryItem.month)
    stmt = stmt.order_by(SalaryItem.month.desc(), SalaryItem.user_id)
    rows = db.execute(stmt).all()
    return [
        {"user_id": r.user_id, "month": r.month, "total_amount": float(r.total_amount), "total_qty": int(r.total_qty)}
        for r in rows
    ]
