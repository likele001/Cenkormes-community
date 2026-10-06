"""cron_jobs 双模式管控（P2-22）回归测试

背景：cron_jobs 为部署级全局单例（非租户隔离），但 admin 接口仅挂租户级
setting.manage 权限 → SaaS 模式下任一租户管理员可改动整个部署的调度
（如关闭日报推送）。

修复：
- 新增平台端 /api/platform/cron-jobs（list/update/reload/defaults，挂
  get_current_platform_user 平台超管）；
- admin 侧写操作（PUT/reload）在 SaaS 模式（saas_mode_enabled=true）返回
  403 并指引平台后台；GET 始终只读可用；
- 私有化模式（默认 saas_mode=false，无平台账号）保持 admin 可写。

覆盖：
- 私有化：admin PUT 成功 / reload 成功 / Redis 失败 500
- SaaS：admin PUT、reload 403（消息指引平台端）；GET 列表与 defaults 只读可用
- 平台端：PUT 成功 / 404 / reload 成功与 Redis 失败 / 未带平台 token 401
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.admin import cron_jobs as admin_cron_jobs
from app.api.platform import cron_jobs as platform_cron_jobs
from app.core.deps import get_current_permissions, get_current_platform_user, get_current_user, get_db
from app.crud.platform_setting import set_setting
from app.models.cron_job import CronJob
from app.models.platform_setting import PlatformSetting  # noqa: F401  注册建表
from app.models.user import User  # noqa: F401


def _mk_job(session, name="daily-report", enabled=True) -> CronJob:
    job = CronJob(name=name, task_name="report.daily", description="工厂日报推送", enabled=enabled, is_system=False)
    session.add(job)
    session.flush()
    return job


@pytest.fixture()
def admin_api(session, test_user):
    app = FastAPI()
    app.include_router(admin_cron_jobs.router, prefix="/admin/cron-jobs")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_permissions] = lambda: ["setting.manage"]
    return TestClient(app)


@pytest.fixture()
def platform_api(session):
    app = FastAPI()
    app.include_router(platform_cron_jobs.router, prefix="/platform/cron-jobs")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_platform_user] = lambda: SimpleNamespace(id=1, username="platform-admin")
    return TestClient(app)


def _enable_saas(session):
    set_setting(session, "saas_mode_enabled", "true")


# ---------------- 私有化模式（saas_mode 默认关闭） ----------------

def test_admin_private_mode_update_ok(admin_api, session, tenant):
    job = _mk_job(session)
    r = admin_api.put(f"/admin/cron-jobs/{job.id}", json={"enabled": False, "cron_minute": "30"})
    assert r.status_code == 200, r.text
    session.refresh(job)
    assert job.enabled is False and job.cron_minute == "30"


def test_admin_private_mode_reload_ok(admin_api, session, monkeypatch):
    _mk_job(session)
    monkeypatch.setattr(admin_cron_jobs, "notify_beat_reload", lambda: True)
    r = admin_api.post("/admin/cron-jobs/reload")
    assert r.status_code == 200
    assert "10 秒" in r.json()["msg"]


def test_admin_private_mode_reload_redis_down(admin_api, session, monkeypatch):
    _mk_job(session)
    monkeypatch.setattr(admin_cron_jobs, "notify_beat_reload", lambda: False)
    r = admin_api.post("/admin/cron-jobs/reload")
    assert r.status_code == 500


# ---------------- SaaS 模式：写收敛平台端 ----------------

def test_admin_saas_mode_update_403(admin_api, session):
    job = _mk_job(session, enabled=True)
    _enable_saas(session)
    r = admin_api.put(f"/admin/cron-jobs/{job.id}", json={"enabled": False})
    assert r.status_code == 403
    assert "平台" in r.json()["detail"]
    session.refresh(job)
    assert job.enabled is True  # 未改动


def test_admin_saas_mode_reload_403(admin_api, session):
    _mk_job(session)
    _enable_saas(session)
    r = admin_api.post("/admin/cron-jobs/reload")
    assert r.status_code == 403
    assert "平台" in r.json()["detail"]


def test_admin_saas_mode_read_only_ok(admin_api, session):
    _mk_job(session)
    _enable_saas(session)
    r1 = admin_api.get("/admin/cron-jobs")
    assert r1.status_code == 200
    assert len(r1.json()["data"]["items"]) == 1  # SaaS 下仍可查看
    r2 = admin_api.get("/admin/cron-jobs/defaults")
    assert r2.status_code == 200


# ---------------- 平台端 ----------------

def test_platform_update_ok(platform_api, session):
    job = _mk_job(session)
    r = platform_api.put(f"/platform/cron-jobs/{job.id}", json={"enabled": False, "cron_hour": "8"})
    assert r.status_code == 200, r.text
    session.refresh(job)
    assert job.enabled is False and job.cron_hour == "8"


def test_platform_update_not_found(platform_api, session):
    r = platform_api.put("/platform/cron-jobs/999999", json={"enabled": False})
    assert r.status_code == 404


def test_platform_reload_ok(platform_api, session, monkeypatch):
    _mk_job(session)
    monkeypatch.setattr(platform_cron_jobs, "notify_beat_reload", lambda: True)
    r = platform_api.post("/platform/cron-jobs/reload")
    assert r.status_code == 200


def test_platform_reload_redis_down(platform_api, session, monkeypatch):
    monkeypatch.setattr(platform_cron_jobs, "notify_beat_reload", lambda: False)
    r = platform_api.post("/platform/cron-jobs/reload")
    assert r.status_code == 500


def test_platform_requires_auth(session):
    """未带平台 token → 401（仅 override get_db，不 override 平台用户）。"""
    app = FastAPI()
    app.include_router(platform_cron_jobs.router, prefix="/platform/cron-jobs")
    app.dependency_overrides[get_db] = lambda: session
    client = TestClient(app)
    assert client.get("/platform/cron-jobs").status_code == 401
    assert client.put("/platform/cron-jobs/1", json={"enabled": False}).status_code == 401
    assert client.post("/platform/cron-jobs/reload").status_code == 401
