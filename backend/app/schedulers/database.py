"""基于数据库的 Celery Beat 调度器

从 cron_jobs 表读取调度配置，支持通过 Redis 信号热重载。
启动命令：
  celery -A app.celery_app.celery beat -S app.schedulers.database:DatabaseScheduler
"""
import logging
import time
from typing import Dict

import redis as redis_lib
from celery.beat import Scheduler
from celery.schedules import crontab
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis 键：写入任意值触发重载
RELOAD_KEY = "celery:beat:reload"
RELOAD_CHECK_INTERVAL = 10  # 秒

# 复用的 Redis 连接（避免每次 tick 新建连接造成泄漏）
_reload_redis = None


def _get_reload_redis():
    global _reload_redis
    if _reload_redis is None:
        _reload_redis = redis_lib.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2, socket_timeout=2
        )
    return _reload_redis


class DatabaseScheduler(Scheduler):
    """从 cron_jobs 表加载调度配置，每 10 秒检查 Redis 重载信号"""

    def __init__(self, app, **kwargs):
        self._engine = None
        self._last_sync: float = 0.0
        self._schedule_dict: Dict[str, dict] = {}
        super().__init__(app, **kwargs)

    def setup_schedule(self):
        """启动时从数据库加载调度配置"""
        db_url = settings.DB_URL
        self._engine = create_engine(
            db_url,
            pool_size=2,
            max_overflow=2,
            pool_pre_ping=True,
        )
        self._load_from_db()

    def _load_from_db(self) -> None:
        """从 cron_jobs 表读取所有启用的任务"""
        from app.models.cron_job import CronJob

        new_schedule: Dict[str, dict] = {}
        try:
            with Session(self._engine) as db:
                stmt = select(CronJob).where(CronJob.enabled == True)
                jobs = db.execute(stmt).scalars().all()
                for job in jobs:
                    new_schedule[job.name] = {
                        "task": job.task_name,
                        "schedule": crontab(
                            minute=job.cron_minute,
                            hour=job.cron_hour,
                            day_of_month=job.cron_day_of_month,
                            month_of_year=job.cron_month_of_year,
                            day_of_week=job.cron_day_of_week,
                        ),
                    }
                self._schedule_dict = new_schedule
                logger.info(
                    "DatabaseScheduler loaded %d enabled cron jobs", len(new_schedule),
                )
        except Exception:
            logger.exception("Failed to load cron jobs from database")

        # 兜底：DB 为空或加载失败时，回退到代码内默认调度，
        # 保证与普通 beat 启动方式（conf.beat_schedule）行为一致
        if not new_schedule:
            from app.celery_app import celery
            new_schedule = dict(celery.conf.beat_schedule or {})
            self._schedule_dict = new_schedule

        # 完全替换而非 merge_inplace：确保 DB 中禁用/删除的任务不再运行。
        # 必须经 _maybe_entry 转为 Entry 对象，否则 tick() 调 is_due() 报
        # "'dict' object has no attribute 'is_due'"
        self.schedule = {
            name: self._maybe_entry(name, entry)
            for name, entry in new_schedule.items()
        }

    def tick(self) -> float:
        """每次 tick 检查 Redis 是否需要重载"""
        now = time.monotonic()
        if now - self._last_sync > RELOAD_CHECK_INTERVAL:
            self._last_sync = now
            try:
                r = _get_reload_redis()
                if r.get(RELOAD_KEY):
                    r.delete(RELOAD_KEY)
                    logger.info("Reload signal received, re-loading schedule from DB")
                    self._load_from_db()
            except Exception:
                pass

        return super().tick()

    def close(self):
        """释放数据库引擎"""
        if self._engine:
            self._engine.dispose()
        super().close()
