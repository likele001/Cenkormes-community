from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import oss2

from app.storage._stream import read_limited_stream
from app.storage.base import StorageError, StoredObject
from app.storage.config import CloudDriverConfig


class AliyunOssStorage:
    driver = "aliyun_oss"

    def __init__(self, cfg: CloudDriverConfig):
        if not cfg.bucket or not cfg.access_key or not cfg.secret_key:
            raise StorageError("阿里云 OSS 配置不完整")
        endpoint = (cfg.endpoint or "").strip()
        if not endpoint:
            region = (cfg.region or "").strip()
            if not region:
                raise StorageError("阿里云 OSS 需配置 endpoint 或 region")
            endpoint = f"https://oss-{region}.aliyuncs.com"
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        self.cfg = cfg
        self.endpoint = endpoint
        auth = oss2.Auth(cfg.access_key, cfg.secret_key)
        self._bucket = oss2.Bucket(auth, endpoint, cfg.bucket)

    def _object_key(self, *, tenant_id: int, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if len(ext) > 16:
            ext = ""
        dt = datetime.now()
        return f"{tenant_id}/{dt:%Y/%m/%d}/{uuid4().hex}{ext}"

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
        headers = {"Content-Type": content_type or "application/octet-stream"}
        self._bucket.put_object(key, data, headers=headers)
        return StoredObject(driver=self.driver, key=key, size=size, sha256=digest)

    def delete(self, *, key: str) -> None:
        self._bucket.delete_object(key)

    def signed_url(
        self,
        *,
        key: str,
        content_type: str,
        expires: int = 3600,
        filename: str | None = None,
    ) -> str:
        params = {}
        if filename:
            from urllib.parse import quote

            params["response-content-disposition"] = f"inline; filename*=UTF-8''{quote(filename)}"
        if content_type:
            params["response-content-type"] = content_type
        url = self._bucket.sign_url("GET", key, expires, params=params or None, slash_safe=True)
        domain = (self.cfg.custom_domain or "").strip().rstrip("/")
        if domain and url:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(url)
            custom = domain if domain.startswith("http") else f"https://{domain}"
            custom_parsed = urlparse(custom)
            url = urlunparse(
                (
                    custom_parsed.scheme or parsed.scheme,
                    custom_parsed.netloc or parsed.netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
        return url

    def resolve_path(self, *, key: str) -> Path:
        raise FileNotFoundError("云存储无本地路径")
