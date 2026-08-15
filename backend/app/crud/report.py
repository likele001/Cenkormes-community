from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.report import Report, ReportAudit


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


def get_report_by_id(db: Session, tenant_id: int, report_id: int) -> Report | None:
    return db.scalar(
        select(Report)
        .where(Report.tenant_id == tenant_id, Report.id == report_id)
        .options(selectinload(Report.task), selectinload(Report.audits), selectinload(Report.report_user))
    )


def list_reports(
    db: Session,
    tenant_id: int,
    task_id: int | None = None,
    report_user_id: int | None = None,
    status: str | None = None,
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
    if status:
        stmt = stmt.where(Report.status == status)
    stmt = stmt.order_by(Report.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


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
