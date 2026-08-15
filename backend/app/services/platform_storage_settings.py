"""平台级文件存储配置（优先 platform_setting，回退 .env）"""

from __future__ import annotations

from io import BytesIO

from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.platform_setting import get_all_settings, get_setting, set_setting
from app.storage.factory import VALID_DRIVERS, build_storage, load_storage_config

SECRET_PLACEHOLDER = "******"

DRIVER_PREFIX = {
    "aliyun_oss": "aliyun_oss",
    "tencent_cos": "tencent_cos",
    "qiniu": "qiniu",
}


def _mask_secret(value: str | None) -> tuple[str, bool]:
    if value:
        return SECRET_PLACEHOLDER, True
    return "", False


def _driver_fields(prefix: str, raw: dict[str, str]) -> dict:
    secret = raw.get(f"storage_{prefix}_secret_key") or ""
    masked, configured = _mask_secret(secret)
    return {
        "endpoint": raw.get(f"storage_{prefix}_endpoint") or "",
        "region": raw.get(f"storage_{prefix}_region") or "",
        "bucket": raw.get(f"storage_{prefix}_bucket") or "",
        "access_key": raw.get(f"storage_{prefix}_access_key") or "",
        "secret_key": masked,
        "secret_key_configured": configured,
        "custom_domain": raw.get(f"storage_{prefix}_custom_domain") or "",
    }


def get_storage_settings_out(db: Session) -> dict:
    raw = get_all_settings(db)
    enabled = str(raw.get("storage_enabled", "false")).lower() in ("1", "true", "yes", "on")
    driver = (raw.get("storage_driver") or settings.STORAGE_DRIVER or "local").lower()
    if driver not in VALID_DRIVERS:
        driver = "local"
    local_backup_enabled = str(raw.get("storage_local_backup_enabled", "false")).lower() in ("1", "true", "yes", "on")
    local_backup_root = raw.get("storage_local_backup_root") or settings.STORAGE_LOCAL_ROOT
    return {
        "storage_enabled": enabled,
        "storage_driver": driver,
        "local_root": settings.STORAGE_LOCAL_ROOT,
        "storage_local_backup_enabled": local_backup_enabled,
        "storage_local_backup_root": local_backup_root,
        "aliyun_oss": _driver_fields("aliyun_oss", raw),
        "tencent_cos": _driver_fields("tencent_cos", raw),
        "qiniu": _driver_fields("qiniu", raw),
    }


def apply_storage_settings(db: Session, payload: dict) -> None:
    if payload.get("storage_enabled") is not None:
        set_setting(db, "storage_enabled", "true" if payload["storage_enabled"] else "false")
    if payload.get("storage_driver") is not None:
        driver = str(payload["storage_driver"]).lower()
        if driver in VALID_DRIVERS:
            set_setting(db, "storage_driver", driver)
    if payload.get("storage_local_backup_enabled") is not None:
        set_setting(db, "storage_local_backup_enabled", "true" if payload["storage_local_backup_enabled"] else "false")
    if payload.get("storage_local_backup_root") is not None:
        root = str(payload["storage_local_backup_root"] or "").strip()
        set_setting(db, "storage_local_backup_root", root)

    for driver_key, prefix in DRIVER_PREFIX.items():
        block = payload.get(driver_key)
        if not isinstance(block, dict):
            continue
        if block.get("secret_key") is not None:
            secret = str(block["secret_key"] or "").strip()
            if secret and secret != SECRET_PLACEHOLDER:
                set_setting(db, f"storage_{prefix}_secret_key", secret)
        for field in ("endpoint", "region", "bucket", "access_key", "custom_domain"):
            if block.get(field) is not None:
                set_setting(db, f"storage_{prefix}_{field}", str(block[field] or "").strip())


def test_storage_connection(db: Session, driver: str | None = None) -> dict:
    cfg = load_storage_config(db)
    use_driver = (driver or cfg.driver).lower()
    if use_driver not in VALID_DRIVERS:
        raise ValueError("不支持的存储驱动")

    cloud_cfg = {
        "aliyun_oss": cfg.aliyun_oss,
        "tencent_cos": cfg.tencent_cos,
        "qiniu": cfg.qiniu,
    }.get(use_driver)
    if cloud_cfg and (not cloud_cfg.access_key or not cloud_cfg.secret_key or not cloud_cfg.bucket):
        raise ValueError("请先填写并保存 AccessKey、SecretKey、Bucket 后再测试")

    storage = build_storage(use_driver, cfg)
    if use_driver == "local":
        root = settings.STORAGE_LOCAL_ROOT
        from pathlib import Path

        p = Path(root)
        p.mkdir(parents=True, exist_ok=True)
        if not p.is_dir():
            raise RuntimeError("本地目录不可写")
        return {"driver": use_driver, "ok": True, "message": "本地目录可用"}

    key = "_platform_test/lightmes_connectivity.txt"
    data = b"lightmes storage test"
    bio = BytesIO(data)
    stored = storage.save(
        tenant_id=0,
        filename="lightmes_connectivity.txt",
        content_type="text/plain",
        stream=bio,
        max_size=1024,
    )
    url = storage.signed_url(key=stored.key, content_type="text/plain", expires=300)
    storage.delete(key=stored.key)
    return {"driver": use_driver, "ok": True, "message": "上传与签名 URL 测试通过", "sample_url": url}
