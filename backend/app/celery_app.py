from celery import Celery

from app.core.config import settings


celery = Celery("lightmes")
celery.conf.update(
    broker_url=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

celery.autodiscover_tasks(["app"])

# 社区版无 CRM / AI / 飞书定时任务；安装 Pro 后由 overlay 覆盖本文件
celery.conf.beat_schedule = {}
