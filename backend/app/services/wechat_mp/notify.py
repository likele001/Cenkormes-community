"""微信小程序订阅消息 - 业务触发 + 推送日志 + Celery 任务入口

业务侧调用：
    from app.services.wechat_mp.notify import emit_wechat_mp_event
    emit_wechat_mp_event(db, tenant_id, event_code, title=..., content=..., user_id=...)

也可以通过统一分发器：
    from app.services.notify_dispatcher import dispatch
    dispatch(db, tenant_id, "report.submitted", title=..., content=..., user_id=...)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_wechat_subscription import UserWechatSubscription
from app.models.wechat_mp_push_log import WechatMpPushLog
from app.services.wechat_mp.client import (
    WechatMpApiError,
    get_access_token,
    send_subscribe_message,
)
from app.services.wechat_mp.settings import (
    get_rule_for_event,
    get_wechat_mp_credentials,
    get_wechat_mp_settings_raw,
    is_wechat_mp_enabled,
)

logger = logging.getLogger(__name__)


# 事件 → 关键词映射（默认顺序）
# 在 admin 后台配置 template_id 后，这里把 content/title 拆成 keyword1/2/3
EVENT_KEYWORDS_HINT: dict[str, list[str]] = {
    "report.submitted":        ["工单号", "提交人", "提交时间", "合格数", "不良数"],
    "report.leader_approved":  ["工单号", "审核人", "审核结果", "时间"],
    "report.qc_approved":      ["工单号", "质检结果", "质检员", "时间"],
    "report.rejected":         ["工单号", "审核人", "驳回原因", "时间"],
    "salary.slip_remind":      ["月份", "应发金额", "状态"],
    "salary.slip_reset":       ["月份", "重置原因", "操作人"],
    "salary.slip_rejected":    ["月份", "拒签原因", "操作人"],
    "dispatch.assigned":       ["工单号", "工序", "数量", "派工人"],
    "order.customer_submitted":["订单号", "客户", "金额", "提交时间"],
    "alert":                   ["告警类型", "告警内容", "时间"],
    "plan.automation_failed":  ["计划号", "失败原因", "时间"],
    "brief.daily":             ["日期", "营收", "待办", "告警"],
}


def _build_data_for_event(
    event_code: str, *, title: str, content: str, extra: dict[str, Any] | None = None
) -> dict[str, Any]:
    """根据 event 把 title/content/extra 塞进 keyword1/2/3/...

    简单实现：keyword1=title, keyword2=content, keyword3..=extra 的 values
    """
    extra = extra or {}
    data: dict[str, Any] = {
        "keyword1": {"value": (title or "")[:20]},
        "keyword2": {"value": (content or "")[:100]},
    }
    idx = 3
    for k, v in extra.items():
        if idx > 5:
            break
        data[f"keyword{idx}"] = {"value": str(v)[:50]}
        idx += 1
    return data


def _resolve_openid(db: Session, user_id: int | None) -> str | None:
    """取用户的微信小程序 openid"""
    if not user_id:
        return None
    u = db.get(User, int(user_id))
    if not u:
        return None
    return (u.wx_miniapp_openid or "").strip() or None


def _has_user_subscribed(
    db: Session,
    *,
    user_id: int,
    event_code: str,
    template_id: str,
    require_accept: bool = True,
) -> bool:
    """检查用户是否订阅过该模板

    - 长期订阅场景：require_accept=False，只要表里有 accept_count > 0 即可
    - 一次性订阅场景：require_accept=True（默认），需要 accept_count > reject_count 且最近 1 次不是拒绝
    """
    row = db.scalar(
        select(UserWechatSubscription).where(
            UserWechatSubscription.user_id == user_id,
            UserWechatSubscription.event_code == event_code,
            UserWechatSubscription.template_id == template_id,
        )
    )
    if not row:
        return False
    if not require_accept:
        return (row.accept_count or 0) > 0
    # 一次性订阅：至少同意过一次，且不是"刚刚拒绝"
    if (row.accept_count or 0) <= 0:
        return False
    # 如果用户最近一次是拒绝，认为当前不可发
    if row.last_rejected_at and (
        not row.last_accepted_at or row.last_rejected_at > row.last_accepted_at
    ):
        # 拒绝过但又同意了 → 仍可发（用户改主意了）
        if (row.accept_count or 0) > (row.reject_count or 0):
            return True
        return False
    return True


def _create_push_log(
    db: Session,
    *,
    tenant_id: int,
    event_code: str,
    target_user_id: int | None,
    openid: str | None,
    title: str,
    content: str,
    template_id: str,
    page: str | None,
    data: dict[str, Any],
) -> WechatMpPushLog:
    row = WechatMpPushLog(
        tenant_id=tenant_id,
        event_code=event_code,
        target_user_id=target_user_id,
        openid=openid,
        template_id=template_id,
        page=page,
        title=title[:128],
        content=content,
        data_json=json.dumps(data, ensure_ascii=False),
        status="pending",
    )
    db.add(row)
    db.flush()
    return row


def enqueue_wechat_mp_push(db: Session, log_id: int) -> None:
    """等当前事务 commit 后再 enqueue，避免 worker 用新 session 查不到未提交的 log。"""
    from app.services.notify_dispatcher import enqueue_after_commit

    enqueue_after_commit(db, "wechat_mp", log_id)


def mark_push_log_result(
    log: WechatMpPushLog,
    *,
    success: bool,
    error_msg: str | None = None,
    message_id: str | None = None,
) -> None:
    log.status = "sent" if success else "failed"
    log.sent_at = datetime.utcnow() if success else None
    log.error_msg = (error_msg or "")[:500]
    log.message_id = message_id
    log.retry_count = (log.retry_count or 0) + (0 if success else 1)


def emit_wechat_mp_event(
    db: Session,
    tenant_id: int,
    event_code: str,
    *,
    title: str,
    content: str,
    user_id: int | None = None,
    extra: dict[str, Any] | None = None,
) -> int:
    """统一入口：业务调用此函数即可（复用飞书/企微的模式）

    Returns: 创建的 push_log 数量
    """
    if not is_wechat_mp_enabled(db, tenant_id):
        return 0
    rule = get_rule_for_event(db, tenant_id, event_code)
    if not rule or not rule.get("enabled", True):
        return 0
    template_id = (rule.get("template_id") or "").strip()
    if not template_id:
        logger.debug("wechat_mp skip: event=%s no template_id", event_code)
        return 0
    openid = _resolve_openid(db, user_id)
    if not openid:
        logger.debug("wechat_mp skip: event=%s user=%s no openid", event_code, user_id)
        return 0
    # 订阅状态校验：避免给没订阅过的用户发（errcode 43101）
    if not _has_user_subscribed(db, user_id=user_id, event_code=event_code, template_id=template_id):
        logger.debug("wechat_mp skip: event=%s user=%s not subscribed", event_code, user_id)
        return 0
    page = rule.get("page") or ""
    data = _build_data_for_event(event_code, title=title, content=content, extra=extra)
    log = _create_push_log(
        db,
        tenant_id=tenant_id,
        event_code=event_code,
        target_user_id=user_id,
        openid=openid,
        title=title,
        content=content,
        template_id=template_id,
        page=page,
        data=data,
    )
    enqueue_wechat_mp_push(db, log.id)
    return 1


def send_wechat_mp_message_by_log(db: Session, log_id: int) -> dict[str, Any]:
    """Celery 任务调用的发送入口（由 tasks.py 注册）"""
    log = db.get(WechatMpPushLog, int(log_id))
    if not log:
        return {"ok": False, "error": "log not found"}
    if log.status == "sent":
        return {"ok": True, "skipped": "already_sent"}
    appid, secret = get_wechat_mp_credentials(db, log.tenant_id)
    if not appid or not secret:
        mark_push_log_result(log, success=False, error_msg="appid/secret not configured")
        db.commit()
        return {"ok": False, "error": "appid/secret not configured"}
    try:
        token = get_access_token(appid, secret)
    except WechatMpApiError as e:
        # token 失效，强制刷新一次
        if e.errcode in (40001, 42001, 40014, 42007):
            try:
                token = get_access_token(appid, secret, force_refresh=True)
            except WechatMpApiError as e2:
                mark_push_log_result(log, success=False, error_msg=f"access_token: {e2.errmsg}")
                db.commit()
                return {"ok": False, "error": e2.errmsg}
        else:
            mark_push_log_result(log, success=False, error_msg=f"access_token: {e.errmsg}")
            db.commit()
            return {"ok": False, "error": e.errmsg}
    cfg = get_wechat_mp_settings_raw(db, log.tenant_id)
    miniprogram_state = cfg.get("miniprogram_state") or "formal"
    data = json.loads(log.data_json or "{}")
    try:
        resp = send_subscribe_message(
            access_token=token,
            openid=log.openid,
            template_id=log.template_id,
            data=data,
            page=log.page or None,
            miniprogram_state=miniprogram_state,
        )
        mark_push_log_result(log, success=True, message_id=str(resp.get("msgid") or ""))
        db.commit()
        return {"ok": True, "message_id": resp.get("msgid")}
    except WechatMpApiError as e:
        mark_push_log_result(log, success=False, error_msg=f"errcode={e.errcode} {e.errmsg}")
        db.commit()
        return {"ok": False, "error": e.errmsg, "errcode": e.errcode}
    except Exception as e:
        mark_push_log_result(log, success=False, error_msg=f"exception: {e!s}"[:500])
        db.commit()
        logger.exception("wechat_mp send error log_id=%s", log_id)
        return {"ok": False, "error": str(e)[:200]}
