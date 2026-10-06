from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_permissions, get_current_user, get_db
from app.core.response import ok
from app.crud.export_job import get_export_job_by_id
from app.models.user import User


router = APIRouter()

# P2-18：导出任务读取权限映射（job_type → 创建入口的业务权限码）
_JOB_PERMISSION_MAP: dict[str, str] = {
    "salary_excel": "salary.manage",
    "finance_statement": "finance.manage",
    "purchase_statement": "purchase.manage",
    "warehouse_stock": "warehouse.manage",
    "report_production": "report.view",
    "report_yield": "report.view",
}


@router.get("/export-jobs/{job_id}")
def get_export_job_api(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    permission_codes: list[str] = Depends(get_current_permissions),
):
    job = get_export_job_by_id(db, tenant_id=user.tenant_id, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="导出任务不存在")
    # P2-18：创建者本人或具备对应业务权限才可读（防同租户越权读薪资等敏感导出结果）
    if job.created_by != user.id:
        perm = _JOB_PERMISSION_MAP.get(job.job_type or "")
        if not perm or perm not in permission_codes:
            raise HTTPException(status_code=403, detail="无权查看该导出任务")
    params = {}
    if job.params_json:
        import json
        try:
            params = json.loads(job.params_json) or {}
        except Exception:
            params = {}
    return ok({
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "params": params,
        "result_attachment_id": job.result_attachment_id,
        "error_msg": job.error_msg,
        "created_by": job.created_by,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    })
