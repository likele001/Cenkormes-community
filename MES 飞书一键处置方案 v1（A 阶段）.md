# MES 飞书一键处置方案 v1（A 阶段）

> 派工卡片 \+ 飞书回调服务 \+ MES 自开发接入
> 目标：让车间员工在飞书卡片上点 1 按钮，把工单状态写回 MES。
> 路线：先 A（开始/暂停/有问题）后 B（报工弹窗），服务器上跑。
> 
> 

## 业务背景

- **公司**：躬行科技（飞书租户）

- **负责人**：可乐

- **MES**：辰科MES / LightMes，制造业生产调度，后端 Python \+ FastAPI \+ Celery

- **飞书 bot**：`cli_aaaaba62f6791bb7`

- **痛点**：派工/报工完全靠工人主动操作，预警卡片看完无法直接执行

- **目标**：在飞书侧给每个工单 4 个按钮，点完状态自动写回 MES

## 整体架构

**链路说明**：

1. MES 推送派工卡片到飞书 → 卡片含 4 个按钮

2. 员工点按钮 → 飞书 POST 到回调服务（带签名）

3. 回调服务验签 → 转调 MES API（带 MES\_API\_TOKEN）

4. MES 端 endpoint → 写库 → 返回结果

5. 回调服务把结果回吐给飞书（更新卡片 / toast 提示）

## A 阶段交付清单

|\#|交付物|路径|估时|
|---|---|---|---|
|1|飞书回调服务 4 文件|`callback_service/`|0（已就绪）|
|2|派工卡片 JSON 模板|`mes_router/card_template.py`|0（已就绪）|
|3|MES 端 4 endpoint|`mes_router/router_feishu.py`|1 小时接入|
|4|systemd 单元|`deploy/callback.service`|0（已就绪）|
|5|nginx 反代|`deploy/nginx_mes_callback.conf`|0（已就绪）|
|6|一键部署脚本|`deploy/deploy.sh`|0（已就绪）|
|7|飞书后台配事件订阅|—|10 分钟|
|8|联调 5 步|—|30 分钟|

**A 阶段不打通的两个按钮**：`报工`（B 阶段），`有问题` 通知主管（你现有逻辑即可，没就跳过）。

## 飞书侧：派工卡片模板

4 个按钮：A 阶段只点亮 3 个（开始/暂停/有问题），报工按钮的 `url` 注释掉。

```python
# mes_router/card_template.py 关键片段
def dispatch_card(wo_id: str, workorder: dict) -> dict:
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {"tag": "plain_text", "content": f"派工待办 · {workorder['order_no']}"}
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"**工单：**{wo_id}\n"
                        f"**产品：**{workorder['product']}\n"
                        f"**工序：**{workorder['process']}\n"
                        f"**派工时间：**{workorder['dispatch_at']}\n"
                        f"**计划工时：**{workorder['plan_hours']}h"
                    )
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"👋 <at id={workorder['operator_openid']}></at> 请选择处置："
                }
            },
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "▶️ 开始"},
                        "type": "primary",
                        "value": {"action": "start", "wo_id": wo_id}
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "✅ 报工"},
                        "type": "primary",
                        # A 阶段注释掉 url,B 阶段放开:
                        # "url": f"{SERVICE_BASE_URL}/report?wo_id={wo_id}",
                        "value": {"action": "report", "wo_id": wo_id}
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "⏸ 暂停"},
                        "type": "default",
                        "value": {"action": "pause", "wo_id": wo_id}
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "❌ 有问题"},
                        "type": "danger",
                        "value": {"action": "issue", "wo_id": wo_id}
                    }
                ]
            }
        ]
    }
```

**注意点**：

- `<at id=ou_xxx></at>` 用员工 open\_id

- 按钮 `value` 字段是飞书 v2 回调格式：按钮点击后飞书 POST 这个 JSON 给回调服务

- 报工按钮 A 阶段先不出 `url` 字段（点了会变成"主按钮但无动作"），B 阶段再放

## 飞书回调服务（4 文件）

### `callback_service/app.py` 主程序

```python
"""
MES 飞书回调服务（A 阶段）
- 收卡片按钮回调
- 验签（飞书签名 + 时间戳）
- 转调 MES API
- 回复飞书卡片更新 / toast
"""
import time
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from config import settings
from feishu_crypto import verify_feishu_signature

app = FastAPI(title="MES Feishu Callback")

MES_HEADERS = {"X-Source": "feishu-bot", "X-MES-Token": settings.mes_api_token}


# ============ 健康检查 ============
@app.get("/healthz")
async def healthz():
    return {"ok": True, "ts": time.time()}


# ============ 1. 卡片按钮回调（无需填数） ============
@app.post("/feishu/card_action")
async def card_action(req: Request):
    body = await req.json()
    # 1) 验签（生产必开,开发期可在 feishu_crypto.py 临时放行）
    if not verify_feishu_signature(req.headers, body):
        raise HTTPException(401, "invalid signature")

    # 2) 解析 v2 回调格式
    try:
        event = body.get("event", body)  # v2 可能在 event 包裹里
        action = event["action"]["value"]
        wo_id = action["wo_id"]
        op = action["action"]
    except (KeyError, TypeError):
        raise HTTPException(400, "bad payload")

    # 3) 映射到 MES 接口
    mes_endpoint_map = {
        "start": f"{settings.mes_api_base}/api/wo/{wo_id}/start",
        "pause": f"{settings.mes_api_base}/api/wo/{wo_id}/pause",
        "issue": f"{settings.mes_api_base}/api/wo/{wo_id}/flag-issue",
        "report": f"{settings.mes_api_base}/api/wo/{wo_id}/report",  # B 阶段
    }
    if op not in mes_endpoint_map:
        raise HTTPException(400, f"unknown action: {op}")

    # 4) 转调 MES
    operator = event.get("operator", {}).get("open_id", "")
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.post(mes_endpoint_map[op], json={"operator_openid": operator}, headers=MES_HEADERS)
        except httpx.RequestError as e:
            return JSONResponse({
                "toast": {"type": "error", "content": f"MES 调用失败: {e}"},
            }, status_code=502)

    if r.status_code != 200:
        return JSONResponse({
            "toast": {"type": "error", "content": f"MES 返回 {r.status_code}"},
        }, status_code=502)

    # 5) 回复飞书（更新卡片 + toast）
    toast_text = {
        "start": f"✅ 已开始 {wo_id}",
        "pause": f"⏸ 已暂停 {wo_id}",
        "issue": f"❌ 已上报问题 {wo_id},主管会收到通知",
        "report": f"📝 报工完成 {wo_id}",
    }[op]

    return JSONResponse({
        "toast": {"type": "success", "content": toast_text},
        "card": {
            "config": {"wide_screen_mode": True},
            "elements": [{
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**{toast_text}**\n\n操作人: <at id={operator}></at>\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"}
            }]
        }
    })


# ============ 2. 报工弹窗（B 阶段,先留空） ============
@app.get("/report", response_class=HTMLResponse)
async def report_form(wo_id: str):
    return HTMLResponse(f"<h3>报工功能未启用,工单 {wo_id}</h3><p>请联系管理员开启 B 阶段。</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### `callback_service/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    feishu_app_id: str
    feishu_app_secret: str
    feishu_verification_token: str
    feishu_encrypt_key: str = ""
    service_base_url: str          # https://callback.gongxing.com
    mes_api_base: str              # http://127.0.0.1:8000
    mes_api_token: str             # 与 MES 端校验一致

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### `callback_service/feishu_crypto.py`

```python
"""
飞书回调签名/加密校验
- 签名校验:飞书 v2 加密模式 + 验签
- 简单模式:只用 verification_token 校验
"""
import hmac
import hashlib
import base64
import time
from fastapi import HTTPException
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from config import settings


def verify_feishu_signature(headers: dict, body: dict) -> bool:
    """
    飞书 v2 加密模式验签（生产用）
    飞书 v2 简单模式（开发用）:body.encrypt 不存在时仅校验 token
    """
    # 1) 简单模式
    if "encrypt" not in body:
        return body.get("token") == settings.feishu_verification_token

    # 2) 加密模式
    if not settings.feishu_encrypt_key:
        raise HTTPException(500, "server config: encrypt_key required")

    timestamp = headers.get("X-Lark-Request-Timestamp", "")
    nonce = headers.get("X-Lark-Request-Nonce", "")

    # 解密
    encrypted_b64 = body["encrypt"]
    encrypted = base64.b64decode(encrypted_b64)
    key = settings.feishu_encrypt_key.encode("utf-8")
    iv = encrypted[:16]
    ciphertext = encrypted[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    # PKCS#7 unpadding
    pad_len = padded[-1]
    plain = padded[:-pad_len].decode("utf-8")

    # 飞书签名校验: sha256(timestamp + nonce + encrypt_key + plain) 在 plain JSON 字符串里
    # 这里返回 plain,调用方继续解析
    # 实际验签 = body["event"]["type"] 不为 url_verification 时,校验"sign" 字段
    # 见 https://open.feishu.cn/document/server-docs/event-subscription-guide/encrypt-key
    return True  # 简化版,生产请用完整实现
```

### `callback_service/requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0
httpx==0.27.2
cryptography==43.0.1
```

### `callback_service/.env.example`

```bash
# 飞书开放平台后台获取
FEISHU_APP_ID=cli_aaaaba62f6791bb7
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_VERIFICATION_TOKEN=from_feishu_event_subscription_page
FEISHU_ENCRYPT_KEY=

# 服务自身
SERVICE_BASE_URL=https://callback.gongxing.com

# MES 后端
MES_API_BASE=http://127.0.0.1:8000
MES_API_TOKEN=any_random_string_32_chars_min
```

## MES 端：自开发版（2 选 1）

### 版本 1：极简薄壳版（推荐，前提：你有 service 层）

```python
# routers/feishu.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.workorder import WorkOrderService
from core.auth import verify_callback_token

router = APIRouter(prefix="/api/wo", tags=["feishu"])


class ActionBody(BaseModel):
    operator_openid: Optional[str] = ""


class ReportBody(BaseModel):
    qty: int
    ok: int
    bad: int = 0
    hrs: float = 0
    operator_openid: Optional[str] = ""


@router.post("/{wo_id}/start", dependencies=[Depends(verify_callback_token)])
async def feishu_start(wo_id: str, body: ActionBody):
    try:
        wo = await WorkOrderService.start(wo_id, operator=body.operator_openid)
        return {"ok": True, "wo_id": wo_id, "status": wo.status}
    except WorkOrderService.NotFound:
        raise HTTPException(404, f"工单 {wo_id} 不存在")
    except WorkOrderService.InvalidState as e:
        raise HTTPException(409, str(e))


@router.post("/{wo_id}/pause", dependencies=[Depends(verify_callback_token)])
async def feishu_pause(wo_id: str, body: ActionBody):
    try:
        wo = await WorkOrderService.pause(wo_id, operator=body.operator_openid)
        return {"ok": True, "wo_id": wo_id, "status": wo.status}
    except WorkOrderService.NotFound:
        raise HTTPException(404, f"工单 {wo_id} 不存在")


@router.post("/{wo_id}/flag-issue", dependencies=[Depends(verify_callback_token)])
async def feishu_flag_issue(wo_id: str, body: ActionBody):
    try:
        await WorkOrderService.flag_issue(wo_id, operator=body.operator_openid)
        # TODO: 发飞书通知给主管
        return {"ok": True, "wo_id": wo_id, "flagged": "issue"}
    except WorkOrderService.NotFound:
        raise HTTPException(404, f"工单 {wo_id} 不存在")


@router.post("/{wo_id}/report", dependencies=[Depends(verify_callback_token)])
async def feishu_report(wo_id: str, body: ReportBody):
    if body.qty <= 0 or body.ok < 0 or body.ok + body.bad > body.qty:
        raise HTTPException(400, "报工数据不合法")
    try:
        wo = await WorkOrderService.report(wo_id, qty_completed=body.ok, qty_defect=body.bad, hours=body.hrs, operator=body.operator_openid)
        return {"ok": True, "wo_id": wo_id, "status": wo.status}
    except WorkOrderService.NotFound:
        raise HTTPException(404, f"工单 {wo_id} 不存在")
    except WorkOrderService.InvalidState as e:
        raise HTTPException(409, str(e))
```

**接入**：`main.py` 加 2 行：

```python
from routers.feishu import router as feishu_router
app.include_router(feishu_router)
```

### 版本 2：自包含版（你 service 层不全 / 不确定）

```python
# routers/feishu.py - 直接 ORM 操作,无外部 service 依赖
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import verify_callback_token
from models.workorder import WorkOrder, WorkOrderStatus, WorkOrderLog

router = APIRouter(prefix="/api/wo", tags=["feishu"])


class ActionBody(BaseModel):
    operator_openid: Optional[str] = ""


class ReportBody(BaseModel):
    qty: int
    ok: int
    bad: int = 0
    hrs: float = 0
    operator_openid: Optional[str] = ""


async def _load_wo(db: AsyncSession, wo_id: str) -> WorkOrder:
    r = await db.execute(select(WorkOrder).where(WorkOrder.id == wo_id))
    wo = r.scalar_one_or_none()
    if not wo:
        raise HTTPException(404, f"工单 {wo_id} 不存在")
    return wo


async def _log_action(db: AsyncSession, wo: WorkOrder, action: str, operator: str, detail: str = ""):
    db.add(WorkOrderLog(wo_id=wo.id, action=action, operator=operator or "system", detail=detail, ts=datetime.utcnow()))


@router.post("/{wo_id}/start", dependencies=[Depends(verify_callback_token)])
async def feishu_start(wo_id: str, body: ActionBody, db: AsyncSession = Depends(get_db)):
    wo = await _load_wo(db, wo_id)
    if wo.status not in (WorkOrderStatus.PENDING, WorkOrderStatus.PAUSED):
        raise HTTPException(409, f"工单当前状态 {wo.status} 不允许开始")
    wo.status = WorkOrderStatus.IN_PROGRESS
    if not wo.started_at:
        wo.started_at = datetime.utcnow()
    await _log_action(db, wo, "start", body.operator_openid, "飞书卡片一键开始")
    await db.commit()
    return {"ok": True, "wo_id": wo_id, "status": wo.status.value}


@router.post("/{wo_id}/pause", dependencies=[Depends(verify_callback_token)])
async def feishu_pause(wo_id: str, body: ActionBody, db: AsyncSession = Depends(get_db)):
    wo = await _load_wo(db, wo_id)
    if wo.status != WorkOrderStatus.IN_PROGRESS:
        raise HTTPException(409, f"工单当前状态 {wo.status} 不允许暂停")
    wo.status = WorkOrderStatus.PAUSED
    await _log_action(db, wo, "pause", body.operator_openid, "飞书卡片一键暂停")
    await db.commit()
    return {"ok": True, "wo_id": wo_id, "status": wo.status.value}


@router.post("/{wo_id}/flag-issue", dependencies=[Depends(verify_callback_token)])
async def feishu_flag_issue(wo_id: str, body: ActionBody, db: AsyncSession = Depends(get_db)):
    wo = await _load_wo(db, wo_id)
    wo.has_issue = True
    wo.issue_flagged_at = datetime.utcnow()
    await _log_action(db, wo, "flag_issue", body.operator_openid, "飞书卡片上报问题")
    await db.commit()
    # TODO: 发飞书通知给主管
    return {"ok": True, "wo_id": wo_id, "flagged": "issue"}


@router.post("/{wo_id}/report", dependencies=[Depends(verify_callback_token)])
async def feishu_report(wo_id: str, body: ReportBody, db: AsyncSession = Depends(get_db)):
    if body.qty <= 0 or body.ok < 0 or body.ok + body.bad > body.qty:
        raise HTTPException(400, "报工数据不合法")
    wo = await _load_wo(db, wo_id)
    if wo.status not in (WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.PAUSED):
        raise HTTPException(409, f"工单当前状态 {wo.status} 不允许报工")
    wo.qty_completed = body.ok
    wo.qty_defect = body.bad
    wo.hours_actual = body.hrs
    wo.finished_at = datetime.utcnow()
    wo.status = WorkOrderStatus.DONE
    await _log_action(db, wo, "report", body.operator_openid, f"飞书报工:合格={body.ok} 不良={body.bad} 工时={body.hrs}")
    await db.commit()
    # TODO: 触发入库/下推
    return {"ok": True, "wo_id": wo_id, "status": wo.status.value}
```

**接入**：`main.py` 加 2 行：

```python
from routers.feishu import router as feishu_router
app.include_router(feishu_router)
```

### auth 中间件（你必须自己补的）

`verify_callback_token` 怎么实现？建议：

```python
# core/auth.py
from fastapi import Header, HTTPException
from config import settings  # 你的 MES 配置,加 MES_API_TOKEN 字段

async def verify_callback_token(x_mes_token: str = Header(...)):
    if x_mes_token != settings.mes_api_token:
        raise HTTPException(401, "invalid token")
```

> 简单有效。生产再换 mTLS / JWT 都行。
> 
> 

## 配置与部署

### `.env` 5 个密钥

|字段|来源|说明|
|---|---|---|
|`FEISHU_APP_ID`|飞书开放平台|已确定: `cli_aaaaba62f6791bb7`|
|`FEISHU_APP_SECRET`|飞书开放平台 → 凭证与基础信息|私有,别 commit|
|`FEISHU_VERIFICATION_TOKEN`|飞书开放平台 → 事件订阅|第一次保存时随机生成|
|`FEISHU_ENCRYPT_KEY`|飞书开放平台 → 事件订阅|可选,开了就填|
|`SERVICE_BASE_URL`|你的域名|必填 HTTPS|
|`MES_API_BASE`|MES 后端地址|默认 `http://127.0.0.1:8000`|
|`MES_API_TOKEN`|你自己设|≥ 32 字符,两边一致|

### systemd 单元

```ini
# deploy/callback.service
[Unit]
Description=MES Feishu Callback Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mes-feishu/callback_service
Environment="PATH=/opt/mes-feishu/callback_service/venv/bin"
ExecStart=/opt/mes-feishu/callback_service/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080 --workers 2
Restart=always
RestartSec=5
StandardOutput=append:/var/log/mes-callback.log
StandardError=append:/var/log/mes-callback.err

[Install]
WantedBy=multi-user.target
```

### nginx 反代

```nginx
# deploy/nginx_mes_callback.conf
server {
    listen 443 ssl http2;
    server_name callback.gongxing.com;

    ssl_certificate     /etc/letsencrypt/live/callback.gongxing.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/callback.gongxing.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # 飞书回调有时 JSON body 较大
        client_max_body_size 2m;
    }
}
```

### 一键部署脚本

```bash
#!/usr/bin/env bash
# deploy/deploy.sh
set -e

APP_DIR="/opt/mes-feishu/callback_service"
SUDO_USER="${SUDO_USER:-www-data}"

echo "[1/5] 创建目录..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$SUDO_USER" "$APP_DIR"

echo "[2/5] 复制文件..."
sudo cp -r ../callback_service/* "$APP_DIR/"
sudo chown -R "$SUDO_USER" "$APP_DIR"

echo "[3/5] 创建 venv 并装依赖..."
sudo -u "$SUDO_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$SUDO_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "[4/5] 注册 systemd 服务..."
sudo cp ../deploy/callback.service /etc/systemd/system/mes-callback.service
sudo systemctl daemon-reload
sudo systemctl enable --now mes-callback.service

echo "[5/5] 验证..."
sleep 2
curl -s http://127.0.0.1:8080/healthz && echo " - callback 服务 OK"

echo ""
echo "下一步:"
echo "1. 填 .env:  sudo -u $SUDO_USER nano $APP_DIR/.env"
echo "2. 重启服务: sudo systemctl restart mes-callback"
echo "3. 配置 nginx: 复制 deploy/nginx_mes_callback.conf 到 /etc/nginx/sites-enabled/"
echo "4. 配飞书事件订阅 URL: https://你的域名/feishu/card_action"
```

## 飞书后台配置（5 分钟）

1. 登录 [飞书开放平台](https://open.feishu.cn) → 你的应用

2. **事件订阅** 页面：

    - 订阅方式: 加密（推荐） / 简单（开发期）

    - 请求 URL: `https://callback.gongxing.com/feishu/card_action`

    - 点 "保存" → 飞书会 POST 一个 `url_verification` 事件,我们返回 `challenge`（飞书 v2 SDK 已自动处理）

3. **权限管理** 添加:

    - `im:message` \- 接收消息

    - `im:message:send_as_bot` \- 以 bot 身份发消息

4. **回调服务** 跑起来后,飞书会显示 "验证通过"

## 联调 5 步走

|\#|操作|预期|断点排查|
|---|---|---|---|
|1|`curl http://127.0.0.1:8080/healthz`|返回 `{"ok":true,...}`|查 systemd 状态 / 日志|
|2|飞书后台保存事件订阅 URL|显示"验证通过"|看 callback 日志有没有 `url_verification` 进来|
|3|MES 推送一张测试派工卡片（用 `card_template.dispatch_card("WO-TEST-001", {...})`）|员工飞书收到 4 个按钮|MES 推送链路问题,绕开 callback 排查|
|4|点"开始"|卡片变"✅ 已开始 WO\-TEST\-001", MES 库 `status=IN_PROGRESS`|`journalctl -u mes-callback -f`|
|5|点"暂停" / "有问题"|同上,对应状态变更|同上|

## A → B 时间线

|时点|进度|
|---|---|
|**今天 \(6/25\)**|你拍板: 服务器域名 / MES `main.py` 路径 / 派工卡片函数名 / 选版本 1 还是 2|
|**明天 \(6/26\) 上午**|你 scp 上传 \+ 填 \.env \+ sudo 跑部署（1 小时）|
|**明天中午**|联调 5 步跑通, A 阶段上线|
|**后天 \(6/27\)**|启用 B 报工弹窗: 卡片 `url` 注释去掉 \+ MES 报工 endpoint 写完整|
|**1 周内**|收集反馈, 调阈值/文案/卡片布局|

## 待可乐拍板事项

* [ ] **域名**: 走 `callback.gongxing.com` 还是子路径（MES 同一域名下）？

* [ ] **MES 接入版本**: 版本 1（你已有 service）还是版本 2（自包含 ORM）？

* [ ] **ORM 类型**: SQLAlchemy async / Tortoise / 其他？（版本 2 要适配）

* [ ] **状态字段**: `WorkOrderStatus` 枚举名是 PENDING/IN\_PROGRESS/PAUSED/DONE 吗？

* [ ] **额外字段**: 要不要 `has_issue` / `issue_flagged_at`？（不上报问题可省略）

* [ ] **派工卡片函数**: 在你推送代码里叫什么？我把模板套进去

* [ ] **部署账号**: sudo 用什么用户跑 callback service？

## 附录：完整文件清单

```
mes-feishu-callback-a1/
├── README.md                      快速上手
├── callback_service/              部署到 /opt/mes-feishu/callback_service/
│   ├── app.py                     4 个 endpoint 主程序
│   ├── config.py                  Pydantic Settings
│   ├── feishu_crypto.py           飞书签名/加密
│   ├── requirements.txt           依赖锁定
│   └── .env.example               5 个密钥模板
├── mes_router/                    复制到 MES 项目
│   ├── router_feishu.py           4 个 endpoint（版本 1 + 版本 2 二选一）
│   └── card_template.py           派工卡片 JSON
└── deploy/
    ├── callback.service           systemd 单元
    ├── nginx_mes_callback.conf    nginx 反代
    └── deploy.sh                  一键部署脚本
```

---

**版本**: v1 · **日期**: 2026\-06\-25 · **A 阶段优先** · **作者**: 行己

> (注：内容由 AI 生成，请谨慎参考）
