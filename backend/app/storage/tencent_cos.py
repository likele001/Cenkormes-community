from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosServiceError

from app.storage._stream import read_limited_stream
from app.storage.base import StorageError, StoredObject
from app.storage.config import CloudDriverConfig


class TencentCosStorage:
    driver = "tencent_cos"

    def __init__(self, cfg: CloudDriverConfig):
        if not cfg.bucket or not cfg.access_key or not cfg.secret_key:
            raise StorageError("腾讯云 COS 配置不完整")
        region = (cfg.region or "").strip()
        if not region:
            raise StorageError("腾讯云 COS 需配置 region")
        self.cfg = cfg
        self.region = region
        cos_cfg = CosConfig(
            Region=region,
            SecretId=cfg.access_key,
            SecretKey=cfg.secret_key,
            Scheme="https",
        )
        self._client = CosS3Client(cos_cfg)

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
        self._client.put_object(
            Bucket=self.cfg.bucket,
            Body=data,
            Key=key,
            ContentType=content_type or "application/octet-stream",
        )
        return StoredObject(driver=self.driver, key=key, size=size, sha256=digest)

    def delete(self, *, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self.cfg.bucket, Key=key)
        except CosServiceError as e:
            if e.get_error_code() not in ("NoSuchKey", "404"):
                raise

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
        url = self._client.get_presigned_url(
            Method="GET",
            Bucket=self.cfg.bucket,
            Key=key,
            Expired=max(60, int(expires)),
            Params=params or None,
        )
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
