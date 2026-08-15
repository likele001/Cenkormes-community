"""微信小程序订阅消息 - 客户端（access_token 缓存 + 发送）"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# 微信 API
WX_API_BASE = "https://api.weixin.qq.com"
ACCESS_TOKEN_URL = f"{WX_API_BASE}/cgi-bin/token"
SUBSCRIBE_SEND_URL = f"{WX_API_BASE}/cgi-bin/message/subscribe/send"

# Redis key 前缀
_ACCESS_TOKEN_KEY = "wechat_mp:access_token:{appid}"


class WechatMpApiError(Exception):
    """微信 API 业务错误"""

    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"wechat_mp api error {errcode}: {errmsg}")


def _get_redis() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_access_token(appid: str, app_secret: str, *, force_refresh: bool = False) -> str:
    """获取 access_token（缓存 110 分钟，微信官方 7200 秒）"""
    r = _get_redis()
    key = _ACCESS_TOKEN_KEY.format(appid=appid)
    try:
        if not force_refresh:
            cached = r.get(key)
            if cached:
                return cached
        # 调用微信
        import httpx
        resp = httpx.get(
            ACCESS_TOKEN_URL,
            params={"grant_type": "client_credential", "appid": appid, "secret": app_secret},
            timeout=10.0,
        )
        data = resp.json()
        if "access_token" not in data:
            raise WechatMpApiError(data.get("errcode", -1), data.get("errmsg", "unknown"))
        token = data["access_token"]
        expires_in = int(data.get("expires_in", 7200))
        # 提前 10 分钟过期，避免临界点
        r.setex(key, max(expires_in - 600, 600), token)
        return token
    finally:
        try:
            r.close()
        except Exception:
            pass


def send_subscribe_message(
    *,
    access_token: str,
    openid: str,
    template_id: str,
    data: dict[str, Any],
    page: str | None = None,
    miniprogram_state: str = "formal",
) -> dict[str, Any]:
    """发送订阅消息

    data 格式：{ "keyword1": {"value": "..."}, "keyword2": {"value": "..."}, ... }
    """
    import httpx

    payload: dict[str, Any] = {
        "touser": openid,
        "template_id": template_id,
        "data": data,
        "miniprogram_state": miniprogram_state,
    }
    if page:
        payload["page"] = page
    resp = httpx.post(
        SUBSCRIBE_SEND_URL,
        params={"access_token": access_token},
        json=payload,
        timeout=10.0,
    )
    body = resp.json()
    if body.get("errcode", 0) != 0:
        # 失效的 token 触发刷新提示
        raise WechatMpApiError(body.get("errcode", -1), body.get("errmsg", "unknown"))
    return body
