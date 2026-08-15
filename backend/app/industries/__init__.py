"""行业包：社区版不包含任何行业包"""
from __future__ import annotations

from app.industries.base import IndustryRegistry


# 社区版注册表为空
registry = IndustryRegistry()


def auto_discover_packs() -> None:
    """社区版不注册任何行业包"""
    pass
