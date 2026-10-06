"""月份区间工具（P3-28）回归测试

背景：`func.date_format(col, "%Y-%m")` 为 MySQL 专有函数，SQLite 测试环境直接
报错（no such function: date_format，即 test_ai_platform 2 个既有失败的根因）。
改为 [月初, 下月初) 范围过滤后语义等价且跨数据库可移植。

覆盖：常规月份 / 12 月跨年 / 1 月 / 非法格式（错误长度、分隔符、越界月份、非数字）。
"""
import pytest

from app.utils.dates import month_range


def test_regular_month():
    start, end = month_range("2026-10")
    assert start.isoformat() == "2026-10-01T00:00:00"
    assert end.isoformat() == "2026-11-01T00:00:00"


def test_december_cross_year():
    start, end = month_range("2026-12")
    assert start.isoformat() == "2026-12-01T00:00:00"
    assert end.isoformat() == "2027-01-01T00:00:00"


def test_january():
    start, end = month_range("2026-01")
    assert start.isoformat() == "2026-01-01T00:00:00"
    assert end.isoformat() == "2026-02-01T00:00:00"


@pytest.mark.parametrize("bad", ["2026-1", "2026-13", "2026-00", "abc", "2026/10", "2026", "", "2026-1a"])
def test_invalid_month_raises(bad):
    with pytest.raises(ValueError):
        month_range(bad)
