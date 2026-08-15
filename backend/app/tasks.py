"""社区版 Celery 任务占位（完整异步任务在 Pro 包）。"""

from celery import shared_task


@shared_task(name="community.health_ping")
def community_health_ping() -> dict:
    return {"edition": "community", "ok": True}
