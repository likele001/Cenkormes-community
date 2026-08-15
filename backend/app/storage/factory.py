"""社区版仅支持本地磁盘存储。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.storage.base import Storage
from app.storage.config import StorageConfig
from app.storage.local import LocalStorage

VALID_DRIVERS = frozenset({"local"})


def load_storage_config(db: Session | None = None) -> StorageConfig:
    return StorageConfig(
        enabled=False,
        driver="local",
        local_root=settings.STORAGE_LOCAL_ROOT,
        aliyun_oss=None,
        tencent_cos=None,
        qiniu=None,
    )


def build_storage(driver: str, cfg: StorageConfig) -> Storage:
    return LocalStorage(cfg.local_root)


def get_active_storage(db: Session) -> Storage:
    cfg = load_storage_config(db)
    return build_storage("local", cfg)


def get_storage_for(driver: str, db: Session | None = None) -> Storage:
    cfg = load_storage_config(db)
    return build_storage("local", cfg)
