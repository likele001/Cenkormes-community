"""社区版 Celery 任务占位。

完整业务任务（CRM/AI/生产/工资/推送/导出）随 Pro 包提供；
社区版仅保留基础装饰器，避免聚合 import 引用 Pro 模块导致启动失败。
"""

from app.tasks import decorators  # noqa: F401
