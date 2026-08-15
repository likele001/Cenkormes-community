"""微信小程序订阅消息 Admin API"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin.system.common import write_op_log
from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.models.user import User
from app.models.wechat_mp_push_log import WechatMpPushLog
from app.services.wechat_mp.client import (
    WechatMpApiError,
    get_access_token,
    send_subscribe_message,
)
from app.services.wechat_mp.notify import EVENT_KEYWORDS_HINT
from app.services.wechat_mp.settings import (
    get_wechat_mp_credentials,
    get_wechat_mp_settings_admin,
    save_wechat_mp_settings,
)

router = APIRouter(dependencies=[Depends(require_permissions(["setting.manage"]))])


class WechatMpSettingsIn(BaseModel):
    enabled: bool | None = None
    appid: str | None = Field(default=None, max_length=64)
    app_secret: str | None = Field(default=None, max_length=128)
    miniprogram_state: str | None = Field(default=None, max_length=16)
    rules: dict | None = None
    quiet_hours: dict | None = None
    default_page: str | None = Field(default=None, max_length=255)


class WechatMpTestSendIn(BaseModel):
    openid: str = Field(min_length=1, max_length=64)
    template_id: str = Field(min_length=1, max_length=128)
    title: str = Field(default="LightMes 微信小程序推送测试", max_length=128)
    content: str = Field(default="这是一条测试推送，验证模板配置是否正确", max_length=500)
    page: str | None = Field(default=None, max_length=255)


@router.get("/wechat-mp")
def get_settings_api(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cfg = get_wechat_mp_settings_admin(db, user.tenant_id)
    return ok({**cfg, "keyword_hints": EVENT_KEYWORDS_HINT})


@router.put("/wechat-mp")
def put_settings_api(
    payload: WechatMpSettingsIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    result = save_wechat_mp_settings(db, tenant_id=user.tenant_id, payload=data)
    write_op_log(
        db,
        request,
        user,
        module="system.setting",
        action="upsert",
        object_type="wechat_mp_notify",
        object_id=user.tenant_id,
        detail="wechat_mp_notify",
    )
    db.commit()
    return ok(result)


@router.post("/wechat-mp/test-connection")
def test_connection_api(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """验证 appid + app_secret 是否能拿到 access_token"""
    appid, secret = get_wechat_mp_credentials(db, user.tenant_id)
    if not appid or not secret:
        raise HTTPException(status_code=400, detail="请先配置 AppID 与 AppSecret")
    try:
        token = get_access_token(appid, secret)
        return ok({"ok": True, "token_preview": token[:12] + "..."})
    except WechatMpApiError as e:
        raise HTTPException(status_code=400, detail=f"errcode={e.errcode} {e.errmsg}") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)[:200]) from e


@router.post("/wechat-mp/test-send")
def test_send_api(
    payload: WechatMpTestSendIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """给指定 openid 发送一条测试订阅消息（不入 push_log）"""
    appid, secret = get_wechat_mp_credentials(db, user.tenant_id)
    if not appid or not secret:
        raise HTTPException(status_code=400, detail="请先配置 AppID 与 AppSecret")
    try:
        token = get_access_token(appid, secret)
        data = {
            "keyword1": {"value": payload.title[:20]},
            "keyword2": {"value": payload.content[:100]},
        }
        body = send_subscribe_message(
            access_token=token,
            openid=payload.openid,
            template_id=payload.template_id,
            data=data,
            page=payload.page,
        )
        return ok({"ok": True, "message_id": body.get("msgid"), "raw": body})
    except WechatMpApiError as e:
        raise HTTPException(status_code=400, detail=f"errcode={e.errcode} {e.errmsg}") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)[:300]) from e


@router.get("/wechat-mp/push-logs")
def list_push_logs_api(
    event_code: str | None = Query(default=None),
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(WechatMpPushLog).where(WechatMpPushLog.tenant_id == user.tenant_id)
    if event_code:
        stmt = stmt.where(WechatMpPushLog.event_code == event_code)
    if status:
        stmt = stmt.where(WechatMpPushLog.status == status)
    stmt = stmt.order_by(WechatMpPushLog.id.desc()).offset(offset).limit(limit)
    rows = db.scalars(stmt).all()
    return ok(
        {
            "items": [
                {
                    "id": r.id,
                    "event_code": r.event_code,
                    "target_user_id": r.target_user_id,
                    "openid": r.openid[:12] + "***",  # 脱敏
                    "template_id": r.template_id,
                    "page": r.page,
                    "title": r.title,
                    "content": (r.content or "")[:200],
                    "status": r.status,
                    "error_msg": (r.error_msg or "")[:200],
                    "message_id": r.message_id,
                    "retry_count": r.retry_count,
                    "created_at": r.created_at,
                    "sent_at": r.sent_at,
                }
                for r in rows
            ]
        }
    )


@router.post("/wechat-mp/push-logs/{log_id}/retry")
def retry_push_log_api(
    log_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.scalar(
        select(WechatMpPushLog).where(WechatMpPushLog.tenant_id == user.tenant_id, WechatMpPushLog.id == log_id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="日志不存在")
    row.status = "pending"
    row.error_msg = None
    row.retry_count = (row.retry_count or 0) + 1
    db.flush()
    try:
        from app.celery_app import celery
        celery.send_task("wechat_mp.send_message", args=[int(log_id)])
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"enqueue failed: {e}") from e
    db.commit()
    return ok({"id": row.id, "status": "pending", "retry_count": row.retry_count})
