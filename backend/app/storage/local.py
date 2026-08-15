from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.storage._stream import read_limited_stream
from app.storage.base import StoredObject, StorageSizeExceeded


class LocalStorage:
    driver = "local"

    def __init__(self, root: str):
        self.root = Path(root).resolve()

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
        abs_path = self.root.joinpath(*key.split("/"))
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        sha256 = __import__("hashlib").sha256()
        size = 0
        try:
            with open(abs_path, "wb") as f:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_size:
                        raise StorageSizeExceeded("文件过大")
                    sha256.update(chunk)
                    f.write(chunk)
        except Exception:
            try:
                if abs_path.exists():
                    os.remove(abs_path)
            finally:
                raise

        return StoredObject(driver=self.driver, key=key, size=size, sha256=sha256.hexdigest(), abs_path=abs_path)

    def delete(self, *, key: str) -> None:
        path = self.resolve_path(key=key)
        if path.exists() and path.is_file():
            os.remove(path)

    def signed_url(
        self,
        *,
        key: str,
        content_type: str,
        expires: int = 3600,
        filename: str | None = None,
    ) -> str:
        raise NotImplementedError("本地存储请通过 /api/files 代理访问")

    def resolve_path(self, *, key: str) -> Path:
        abs_path = self.root.joinpath(*key.split("/")).resolve()
        try:
            abs_path.relative_to(self.root)
        except ValueError:
            raise FileNotFoundError("非法路径")
        return abs_path
