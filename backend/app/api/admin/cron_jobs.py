"""
定时任务管理 API（租户管理端）

- GET /admin/cron-jobs — 列表（始终只读可用）
- PUT /admin/cron-jobs/{id} — 更新（私有化模式可写；SaaS 模式 403 收敛平台端）
- POST /admin/cron-jobs/reload — 手动触发重载（同上）
- GET /admin/cron-jobs/defaults — 获取系统默认任务定义

审计 P2-22：cron_jobs 为部署级全局单例（非租户隔离），SaaS 模式下
任一租户管理员改动会波及整个部署的调度，因此写操作收敛到平台端
/api/platform/cron-jobs（挂平台超管）；私有化部署无平台账号，保持可写。
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_permissions
from app.core.response import ok
from app.crud.cron_job import get_cron_job, list_cron_jobs, notify_beat_reload, update_cron_job
from app.crud.platform_setting import is_saas_mode_enabled

# 定时任务属系统级配置，仅允许拥有 setting.manage 权限的角色（如管理员）操作
router = APIRouter(dependencies=[Depends(require_permissions(["setting.manage"]))])

SAAS_BLOCK_MSG = "定时任务为部署级全局配置，SaaS 模式下请由平台管理员在「平台后台 → 定时任务」管理"


class CronJobUpdateIn(BaseModel):
    enabled: bool | None = None
    cron_minute: str | None = Field(None, max_length=10)
    cron_hour: str | None = Field(None, max_length=10)
    cron_day_of_month: str | None = Field(None, max_length=10)
    cron_month_of_year: str | None = Field(None, max_length=10)
    cron_day_of_week: str | None = Field(None, max_length=10)
    description: str | None = Field(None, max_length=255)


@router.get("")
def list_cron_jobs_api(db: Session = Depends(get_db)):
    """获取所有定时任务（只读，任何模式可用）"""
    jobs = list_cron_jobs(db)
    return ok({"items": [j.to_dict() for j in jobs]})


@router.put("/{job_id}")
def update_cron_job_api(job_id: int, data: CronJobUpdateIn, db: Session = Depends(get_db)):
    """更新定时任务配置（SaaS 模式收敛平台端），成功后通知 Beat 重载"""
    if is_saas_mode_enabled(db):
        raise HTTPException(status_code=403, detail=SAAS_BLOCK_MSG)
    job = get_cron_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    update_cron_job(db, job, data.model_dump(exclude_unset=True))
    notify_beat_reload()  # 失败静默：Beat 重启后仍会从 DB 加载
    return ok(job.to_dict(), msg="保存成功，调度器将在 10 秒内生效")


@router.post("/reload")
def reload_cron_jobs_api(db: Session = Depends(get_db)):
    """手动触发 Beat 重新加载调度配置（10秒内生效；SaaS 模式收敛平台端）"""
    if is_saas_mode_enabled(db):
        raise HTTPException(status_code=403, detail=SAAS_BLOCK_MSG)
    if not notify_beat_reload():
        raise HTTPException(status_code=500, detail="重载信号发送失败（Redis 不可用）")
    return ok(None, msg="重载信号已发送，调度器将在 10 秒内重新加载")


@router.get("/defaults")
def get_default_cron_jobs():
    """返回系统默认任务定义（用于前端参考）"""
    from app.celery_app import DEFAULT_CRON_JOBS
    return ok(DEFAULT_CRON_JOBS)
