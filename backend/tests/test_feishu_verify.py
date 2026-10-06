"""飞书事件回调验签（P2-17）回归测试

背景：`parse_event_body` 在无 encrypt_key 时原样放行，且全链路无 verification_token 校验
（wecom/dingtalk 已验签）→ 任何人可伪造飞书回调（卡片操作、消息事件）。

修复：`verify_event_token` 在回调入口校验 verification_token——
租户配置了该 token 时强制校验（不匹配 403）；未配置时放行（兼容旧部署）。

覆盖：
- 未配置 token：放行（url_verification 挑战正常返回）
- 明文事件 + 顶层 token（url_verification 风格）正确 → 放行
- 明文事件 + header.token（新版事件风格）正确 → 放行
- token 错误 / 缺失 → 403
- 加密 body：解密后校验（正确 token 放行、错误 token 403）
- 空 token 配置 → 不强制校验
"""
from __future__ import annotations

import base64
import hashlib
import json

import pytest
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.feishu import router as feishu_router_module
from app.core.deps import get_db
from app.crud.tenant_setting import upsert_setting

VT = "vt-secret"
EK = "ek-demo"


def _set_cfg(session, tenant_id: int, **kw) -> None:
    cfg = {"enabled": True, "tenant_key": "tk-demo", "verification_token": VT, "encrypt_key": EK}
    cfg.update(kw)
    upsert_setting(session, tenant_id=tenant_id, key="feishu.notify", value=json.dumps(cfg))


def _encrypt(encrypt_key: str, payload: dict) -> str:
    """与 _decrypt_feishu_event 对应的 AES-CBC 加密（IV 前置）。"""
    key = hashlib.sha256(encrypt_key.encode()).digest()
    iv = b"0123456789abcdef"
    padder = PKCS7(128).padder()
    padded = padder.update(json.dumps(payload).encode()) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(iv + enc.update(padded) + enc.finalize()).decode()


@pytest.fixture()
def api(session):
    app = FastAPI()
    app.include_router(feishu_router_module.router, prefix="/api/feishu")
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app)


def _url_verification(token: str = VT) -> dict:
    return {"type": "url_verification", "challenge": "ch-1", "token": token}


def test_no_token_configured_allows(api, session, tenant):
    """未配置任何飞书设置 → 无 token 校验，挑战正常返回。"""
    r = api.post("/api/feishu/events", json=_url_verification())
    assert r.status_code == 200, r.text
    assert r.json()["challenge"] == "ch-1"


def test_blank_token_config_allows(api, session, tenant):
    """配置了设置但 verification_token 为空 → 不强制校验。"""
    _set_cfg(session, tenant.id, verification_token="")
    r = api.post("/api/feishu/events", json=_url_verification(token=""))
    assert r.status_code == 200, r.text
    assert r.json()["challenge"] == "ch-1"


def test_correct_top_token_allows(api, session, tenant):
    """url_verification 风格（顶层 token）正确 → 放行。"""
    _set_cfg(session, tenant.id)
    r = api.post("/api/feishu/events", json=_url_verification())
    assert r.status_code == 200, r.text
    assert r.json()["challenge"] == "ch-1"


def test_correct_header_token_allows(api, session, tenant):
    """新版事件风格（header.token）正确 → 放行。"""
    _set_cfg(session, tenant.id)
    event = {
        "header": {"event_type": "unknown.event", "token": VT, "tenant_key": "tk-demo"},
        "event": {},
    }
    r = api.post("/api/feishu/events", json=event)
    assert r.status_code == 200, r.text


def test_wrong_token_rejected(api, session, tenant):
    """token 错误 → 403。"""
    _set_cfg(session, tenant.id)
    r = api.post("/api/feishu/events", json=_url_verification(token="bad-token"))
    assert r.status_code == 403
    assert "verification_token" in r.json()["detail"]


def test_missing_token_rejected(api, session, tenant):
    """配置了 token 但请求不带 → 403。"""
    _set_cfg(session, tenant.id)
    r = api.post("/api/feishu/events", json={"type": "url_verification", "challenge": "ch-1"})
    assert r.status_code == 403


def test_encrypted_body_verified(api, session, tenant):
    """加密 body：解密后校验（正确 token 放行、错误 token 403）。"""
    _set_cfg(session, tenant.id)
    ok_body = {"encrypt": _encrypt(EK, _url_verification())}
    r = api.post("/api/feishu/events", json=ok_body)
    assert r.status_code == 200, r.text
    assert r.json()["challenge"] == "ch-1"

    bad_body = {"encrypt": _encrypt(EK, _url_verification(token="bad"))}
    r2 = api.post("/api/feishu/events", json=bad_body)
    assert r2.status_code == 403


def test_card_action_wrong_token_rejected(api, session, tenant):
    """卡片回调伪造（header.token 错误）→ 403，不执行任何操作。"""
    _set_cfg(session, tenant.id)
    event = {
        "header": {"event_type": "card.action.trigger", "token": "forged"},
        "event": {"action": {"value": {"action": "report_reject", "biz_type": "report", "biz_id": 1}}},
    }
    r = api.post("/api/feishu/events", json=event)
    assert r.status_code == 403
