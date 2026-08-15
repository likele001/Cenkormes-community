"""Redis 连接（可选）；不可用时返回 None，验证码等可降级内存。"""

from __future__ import annotations

import time

import redis

from app.core.config import settings

_client: redis.Redis | None | bool = None
_last_fail_ts: float = 0.0
RETRY_INTERVAL = 30  # 秒：失败后每 30 秒重试一次，避免 Redis 恢复后永久降级


def get_redis() -> redis.Redis | None:
    global _client, _last_fail_ts
    if _client is False:
        # 已进入降级态：周期重试，Redis 恢复后自动重连
        if time.monotonic() - _last_fail_ts < RETRY_INTERVAL:
            return None
    if isinstance(_client, redis.Redis):
        return _client
    try:
        c = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        c.ping()
        _client = c
        return c
    except Exception:
        _client = False
        _last_fail_ts = time.monotonic()
        return None
