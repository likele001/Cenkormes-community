"""WebSocket 连接池：按租户推送大屏/看板刷新事件"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class DashboardWSHub:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, tenant_id: int, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(tenant_id, set()).add(ws)

    async def disconnect(self, tenant_id: int, ws: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(tenant_id)
            if not room:
                return
            room.discard(ws)
            if not room:
                self._rooms.pop(tenant_id, None)

    async def broadcast(self, tenant_id: int, payload: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._rooms.get(tenant_id, set()))
        if not targets:
            return
        text = json.dumps(payload, ensure_ascii=False)
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                room = self._rooms.get(tenant_id)
                if room:
                    for ws in dead:
                        room.discard(ws)

    async def broadcast_all(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            tenant_ids = list(self._rooms.keys())
        for tid in tenant_ids:
            await self.broadcast(tid, payload)


dashboard_ws_hub = DashboardWSHub()


def broadcast_sync(tenant_id: int, payload: dict[str, Any]) -> None:
    """同步上下文广播（供 FastAPI 同步端点调用），失败不影响主流程。"""
    try:
        asyncio.run(dashboard_ws_hub.broadcast(tenant_id, payload))
    except RuntimeError:
        # 已在运行中的事件循环（async 端点）：改为投递任务
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(dashboard_ws_hub.broadcast(tenant_id, payload))
    except Exception:
        pass
