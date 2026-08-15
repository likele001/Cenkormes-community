from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from qiniu import Auth, put_data

from app.storage._stream import read_limited_stream
from app.storage.base import StorageError, StoredObject
from app.storage.config import CloudDriverConfig


class QiniuKodoStorage:
    driver = "qiniu"

    def __init__(self, cfg: CloudDriverConfig):
        if not cfg.bucket or not cfg.access_key or not cfg.secret_key:
            raise StorageError("七牛 Kodo 配置不完整")
        self.cfg = cfg
        self._auth = Auth(cfg.access_key, cfg.secret_key)

    def _object_key(self, *, tenant_id: int, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if len(ext) > 16:
            ext = ""
        dt = datetime.now()
        return f"{tenant_id}/{dt:%Y/%m/%d}/{uuid4().hex}{ext}"

    def _download_base(self, key: str) -> str:
        domain = (self.cfg.custom_domain or self.cfg.endpoint or "").strip().rstrip("/")
        if not domain:
            region = (self.cfg.region or "z0").strip()
            domain = f"https://{self.cfg.bucket}.{region}.qiniucs.com"
        elif not domain.startswith("http"):
            domain = f"https://{domain}"
        return f"{domain}/{key}"

    def save(
        self,
        *,
        tenant_id: int,
        filename: str,
        content_type: str,
        stream,
        max_size: int,
    ) -> StoredObject:
        key = self._object_key(tenant_id=tenant_id, filename=filename)
        data, size, digest = read_limited_stream(stream, max_size=max_size)
        token = self._auth.upload_token(self.cfg.bucket, key, 3600)
        ret, info = put_data(token, key, data, mime_type=content_type or "application/octet-stream")
        if info.status_code >= 400:
            err = (info.error or info.text_body or str(info)).lower()
            if "badtoken" in err or "bad token" in err:
                raise StorageError(
                    "七牛上传失败：密钥无效（BadToken）。请检查 AccessKey/SecretKey 是否正确、是否已先保存配置，且不要把 AK/SK 填反"
                )
            raise StorageError(f"七牛上传失败: {info.error}")
        return StoredObject(driver=self.driver, key=key, size=size, sha256=digest)

    def delete(self, *, key: str) -> None:
        from qiniu import BucketManager

        bucket_manager = BucketManager(self._auth)
        ret, info = bucket_manager.delete(self.cfg.bucket, key)
        if info.status_code >= 400 and info.status_code != 612:
            raise StorageError(f"七牛删除失败: {info.error}")

    def signed_url(
        self,
        *,
        key: str,
        content_type: str,
        expires: int = 3600,
        filename: str | None = None,
    ) -> str:
        base = self._download_base(key)
        return self._auth.private_download_url(base, expires=max(60, int(expires)))

    def resolve_path(self, *, key: str) -> Path:
        raise FileNotFoundError("云存储无本地路径")
