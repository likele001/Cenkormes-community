from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.crud.notification import create_notification
from app.crud.report import (
    create_audit,
    get_report_by_id,
    list_reports,
    update_report_status,
)
from app.models.user import User


router = APIRouter(dependencies=[Depends(require_permissions(["report.audit"]))])


def _report_out(x) -> dict:
    return {
        "id": x.id,
        "tenant_id": x.tenant_id,
        "task_id": x.task_id,
        "report_user_id": x.report_user_id,
        "good_qty": x.good_qty,
        "bad_qty": x.bad_qty,
        "remark": x.remark,
        "attachment_ids": x.attachment_ids,
        "status": x.status,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "task": (
            {
                "id": x.task.id,
                "task_code": x.task.task_code,
                "process_id": x.task.process_id,
            }
            if hasattr(x, "task") and x.task
            else None
        ),
        "report_user": (
            {"id": x.report_user.id, "full_name": x.report_user.full_name}
            if hasattr(x, "report_user") and x.report_user
            else None
        ),
    }


@router.get("")
def list_api(
    task_id: int | None = Query(default=None, ge=1),
    report_user_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = list_reports(
        db, tenant_id=user.tenant_id,
        task_id=task_id, report_user_id=report_user_id,
        status=status, offset=offset, limit=limit,
    )
    return ok({
        "items": [
            {
                "id": r.id,
                "task_id": r.task_id,
                "report_user_id": r.report_user_id,
                "good_qty": r.good_qty,
                "bad_qty": r.bad_qty,
                "remark": r.remark,
                "attachment_ids": r.attachment_ids,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "report_user": (
                    {"id": r.report_user.id, "full_name": r.report_user.full_name}
                    if hasattr(r, "report_user") and r.report_user
                    else None
                ),
                "task": (
                    {
                        "id": r.task.id,
                        "task_code": r.task.task_code,
                        "process_id": r.task.process_id,
                    }
                    if hasattr(r, "task") and r.task
                    else None
                ),
            }
            for r in items
        ]
    })


@router.get("/{report_id}")
def get_api(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = get_report_by_id(db, tenant_id=user.tenant_id, report_id=report_id)
    if not item:
        raise HTTPException(status_code=400, detail="报工记录不存在")
    data = _report_out(item)
    data["audits"] = [
        {
            "id": a.id,
            "auditor_id": a.auditor_id,
            "audit_level": a.audit_level,
            "action": a.action,
            "reason": a.reason,
            "created_at": a.created_at,
        }
        for a in item.audits
    ]
    return ok(data)


@router.post("/{report_id}/leader-approve")
def leader_approve_api(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = get_report_by_id(db, tenant_id=user.tenant_id, report_id=report_id)
    if not report:
        raise HTTPException(status_code=400, detail="报工记录不存在")
    if report.status != "submitted":
        raise HTTPException(status_code=400, detail="报工状态不允许操作")
    create_audit(db, tenant_id=user.tenant_id, report_id=report.id,
                 auditor_id=user.id, audit_level="leader", action="approve", reason=None)
    update_report_status(db, report, "leader_approved")
    create_notification(
        db,
        tenant_id=user.tenant_id,
        user_id=report.report_user_id,
        title="报工已初审通过",
        content=f"报工 {report.id} 已由班组长初审通过",
        level="info",
        biz_type="report",
        biz_id=report.id,
    )
    db.commit()
    return ok({"report_id": report.id, "status": "leader_approved"})


@router.post("/{report_id}/qc-approve")
def qc_approve_api(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = get_report_by_id(db, tenant_id=user.tenant_id, report_id=report_id)
    if not report:
        raise HTTPException(status_code=400, detail="报工记录不存在")
    if report.status != "leader_approved":
        raise HTTPException(status_code=400, detail="报工状态不允许终审操作")
    create_audit(db, tenant_id=user.tenant_id, report_id=report.id,
                 auditor_id=user.id, audit_level="qc", action="approve", reason=None)
    update_report_status(db, report, "qc_approved")
    create_notification(
        db,
        tenant_id=user.tenant_id,
        user_id=report.report_user_id,
        title="报工已终审通过",
        content=f"报工 {report.id} 已终审通过",
        level="info",
        biz_type="report",
        biz_id=report.id,
    )
    db.commit()
    return ok({"report_id": report.id, "status": "qc_approved"})


@router.post("/{report_id}/reject")
def reject_api(
    report_id: int,
    reason: str | None = Query(default=None, max_length=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = get_report_by_id(db, tenant_id=user.tenant_id, report_id=report_id)
    if not report:
        raise HTTPException(status_code=400, detail="报工记录不存在")
    if report.status not in ("submitted", "leader_approved"):
        raise HTTPException(status_code=400, detail="报工状态不允许驳回")
    create_audit(db, tenant_id=user.tenant_id, report_id=report.id,
                 auditor_id=user.id, audit_level="qc", action="reject", reason=reason)
    update_report_status(db, report, "rejected")
    create_notification(
        db,
        tenant_id=user.tenant_id,
        user_id=report.report_user_id,
        title="报工被驳回",
        content=f"报工 {report.id} 被驳回：{reason or '无原因'}",
        level="warning",
        biz_type="report",
        biz_id=report.id,
    )
    db.commit()
    return ok({"report_id": report.id, "status": "rejected"})
