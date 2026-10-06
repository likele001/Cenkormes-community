from app.storage.base import Storage
from app.storage.factory import get_active_storage, get_storage_for, load_storage_config
from app.storage.local import LocalStorage

__all__ = [
    "Storage",
    "LocalStorage",
    "get_storage",
    "get_active_storage",
    "get_storage_for",
    "load_storage_config",
]


def get_storage() -> Storage:
    """无 DB 会话时的兼容入口，配置来自 .env。"""
    from app.storage.factory import build_storage, load_storage_config

    cfg = load_storage_config(None)
    return build_storage(cfg.driver, cfg)
