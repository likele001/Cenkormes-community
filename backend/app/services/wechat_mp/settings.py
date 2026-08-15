"""微信小程序订阅消息 - 租户配置存储（tenant_settings）

支持的事件类型（与飞书一致，便于复用业务触发点）：
  - report.submitted           报工已提交
  - report.leader_approved     班组长已审
  - report.qc_approved         QC 已审
  - report.rejected            审核拒签
  - salary.slip_remind         工资单提醒
  - salary.slip_reset          工资单重置
  - salary.slip_rejected       工资单拒签
  - dispatch.assigned          派工通知
  - order.customer_submitted   客户订单
  - alert                      告警
  - plan.automation_failed     排产失败

每个 event 在 rules 里可独立开关 / 配 template_id / 配跳转页。
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from sqlalchemy.orm import Session

from app.crud.tenant_setting import get_setting, upsert_setting

KEY = "wechat_mp.notify"
SECRET_MASK = "********"


# 默认规则：模板 ID 留空（用户在 admin 后台填入微信公众平台申请的 template_id）
#
# audience 字段说明：
#   "employee" — 员工向事件（小程序端订阅）
#   "admin"    — 管理员/主管向事件（PC 后台订阅）
#   "both"     — 双端可订阅（如工资拒签，财务和管理端都要看）
DEFAULT_RULES: dict[str, dict[str, Any]] = {
    "report.submitted": {
        "enabled": True,
        "audience": "admin",
        "targets": ["dept_leaders", "workshop_leaders"],
        "template_id": "",
        "page": "pages-admin/audit/batch-list/index",
    },
    "report.leader_approved": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/report/history/index",
    },
    "report.qc_approved": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/salary/index/index",
    },
    "report.rejected": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/report/history/index",
    },
    "salary.slip_remind": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/salary/index/index",
    },
    "salary.slip_reset": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/salary/index/index",
    },
    "salary.slip_rejected": {
        "enabled": True,
        "audience": "admin",
        "targets": ["boss", "group:management"],
        "template_id": "",
        "page": "pages-admin/dashboard/exec/index",
    },
    "dispatch.assigned": {
        "enabled": True,
        "audience": "employee",
        "targets": ["assigned_employee"],
        "template_id": "",
        "page": "pages-employee/task/detail/index",
    },
    "order.customer_submitted": {
        "enabled": True,
        "audience": "admin",
        "targets": ["permission:order.manage", "group:management"],
        "template_id": "",
        "page": "pages-customer/order/detail/index",
    },
    "alert": {
        "enabled": True,
        "audience": "admin",
        "targets": ["boss"],
        "template_id": "",
        "page": "pages-admin/dashboard/exec/index",
    },
    "plan.automation_failed": {
        "enabled": True,
        "audience": "admin",
        "targets": ["permission:plan.manage"],
        "template_id": "",
        "page": "pages-admin/master/index/index",
    },
    "brief.daily": {
        "enabled": True,
        "audience": "admin",
        "targets": ["boss"],
        "template_id": "",
        "page": "pages-admin/dashboard/exec/index",
    },
}


DEFAULT_CONFIG: dict[str, Any] = {
    "enabled": False,
    "appid": "",          # 微信小程序 AppID（也可在 manifest 读，但放数据库便于多租户）
    "app_secret": "",     # 微信小程序 AppSecret
    "miniprogram_state": "formal",   # formal / trial / developer
    "rules": deepcopy(DEFAULT_RULES),
    "quiet_hours": {"enabled": False, "start": "22:00", "end": "08:00"},
    "default_page": "pages-employee/dashboard/index",  # 兜底跳转页
}


def _mask(secret: str | None) -> str:
    if not secret:
        return ""
    s = str(secret)
    if len(s) <= 8:
        return SECRET_MASK
    return s[:4] + SECRET_MASK + s[-4:]


def get_wechat_mp_settings_raw(db: Session, tenant_id: int) -> dict[str, Any]:
    """读取原始配置（不解密、不脱敏）"""
    item = get_setting(db, tenant_id, KEY)
    if not item or not getattr(item, "value", None):
        return deepcopy(DEFAULT_CONFIG)
    try:
        cfg = json.loads(item.value)
    except Exception:
        cfg = {}
    # 合并默认值（保证新增 event / 新增 audience 也能取到）
    base = deepcopy(DEFAULT_CONFIG)
    base.update(cfg or {})
    base["rules"] = {**DEFAULT_CONFIG["rules"], **(cfg or {}).get("rules", {})}
    # 补充已有规则缺失的 audience 字段
    for ev, rule in base["rules"].items():
        if "audience" not in rule and ev in DEFAULT_RULES:
            rule["audience"] = DEFAULT_RULES[ev].get("audience", "both")
    return base


def get_wechat_mp_settings_admin(db: Session, tenant_id: int) -> dict[str, Any]:
    """读取 admin 配置（secret 脱敏）"""
    cfg = get_wechat_mp_settings_raw(db, tenant_id)
    cfg = deepcopy(cfg)
    if cfg.get("app_secret"):
        cfg["app_secret_masked"] = _mask(cfg["app_secret"])
        cfg["app_secret"] = ""  # 不返回明文
    return cfg


def get_wechat_mp_credentials(db: Session, tenant_id: int) -> tuple[str, str]:
    """取 appid + app_secret（不脱敏）"""
    cfg = get_wechat_mp_settings_raw(db, tenant_id)
    return (cfg.get("appid") or "").strip(), (cfg.get("app_secret") or "").strip()


def is_wechat_mp_enabled(db: Session, tenant_id: int) -> bool:
    cfg = get_wechat_mp_settings_raw(db, tenant_id)
    if not cfg.get("enabled"):
        return False
    appid, secret = cfg.get("appid") or "", cfg.get("app_secret") or ""
    return bool(appid.strip() and secret.strip())


def save_wechat_mp_settings(db: Session, *, tenant_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """保存配置；如果 secret 是 ****** 则保留旧值"""
    cur = get_wechat_mp_settings_raw(db, tenant_id)
    app_secret_in = (payload.get("app_secret") or "").strip()
    if app_secret_in == SECRET_MASK or app_secret_in == "":
        # 保留旧 secret
        payload["app_secret"] = cur.get("app_secret", "")
    cur.update(payload or {})
    # 合并 rules（只覆盖传入的）
    if payload.get("rules"):
        merged_rules = deepcopy(cur.get("rules") or {})
        for ev, rule in (payload.get("rules") or {}).items():
            if not isinstance(rule, dict):
                continue
            base = deepcopy(merged_rules.get(ev) or {})
            base.update(rule)
            merged_rules[ev] = base
        cur["rules"] = merged_rules
    # 持久化
    upsert_setting(db, tenant_id, KEY, json.dumps(cur, ensure_ascii=False))
    return get_wechat_mp_settings_admin(db, tenant_id)


def get_rule_for_event(db: Session, tenant_id: int, event_code: str) -> dict[str, Any] | None:
    cfg = get_wechat_mp_settings_raw(db, tenant_id)
    rules = cfg.get("rules") or {}
    if event_code in rules:
        return rules[event_code]
    if event_code.startswith("alert") and "alert" in rules:
        return rules["alert"]
    return None
