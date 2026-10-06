"""日期区间工具（跨数据库可移植）。

背景：`func.date_format(col, "%Y-%m") == "YYYY-MM"` 为 MySQL 专有函数，
SQLite 等环境直接报错（既有测试失败根因）。改为「范围过滤」：
`col >= 月初 AND col < 下月初`，语义等价且全数据库通用。
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """naive UTC 当前时间（替代已弃用的 `datetime.utcnow()`，语义完全一致）。

    Python 3.12 起 `datetime.utcnow()` 发出 DeprecationWarning。
    数据库列为无时区 DATETIME，故此处仍返回 naive 值（去掉 tzinfo）。
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def month_range(month: str) -> tuple[datetime, datetime]:
    """'YYYY-MM' → [月初, 下月初) 左闭右开区间；格式非法抛 ValueError。

    - 严格两位月份（'2026-1' 视为非法，与 date_format 比较的旧行为一致）。
    - 12 月自动跨年。
    """
    if len(month) != 7 or month[4] != "-":
        raise ValueError(f"月份格式应为 YYYY-MM：{month!r}")
    year, mon = int(month[:4]), int(month[5:])
    if not (1 <= mon <= 12):
        raise ValueError(f"月份非法：{month!r}")
    start = datetime(year, mon, 1)
    end = datetime(year + 1, 1, 1) if mon == 12 else datetime(year, mon + 1, 1)
    return start, end
