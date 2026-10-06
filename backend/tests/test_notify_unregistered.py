"""P2-19：通知分发未注册事件不静默（logging warning 告警）回归测试

背景：设置页可配置的事件码若未在 notify_channels 的四个分类集合
（PERSONAL/GROUP_ONLY/MIXED/RULE_BASED）中注册，dispatch 此前会在结尾
静默 return 0，表现为"页面显示配置成功、实际一条推送不发"。
修复：结尾对未注册事件记录 warning（含 event_code/tenant_id/title），便于排查。
"""

from __future__ import annotations

import logging

import pytest
from sqlalchemy.orm import Session

from app.services.notify_channels import (
    GROUP_ONLY_EVENTS,
    MIXED_EVENTS,
    PERSONAL_EVENTS,
    RULE_BASED_EVENTS,
)
from app.services.notify_dispatcher import dispatch

LOGGER_NAME = "app.services.notify_dispatcher"
MARKER = "unregistered event_code="

ALL_REGISTERED = sorted(PERSONAL_EVENTS | GROUP_ONLY_EVENTS | MIXED_EVENTS | RULE_BASED_EVENTS)


def _unregistered_warnings(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if MARKER in r.getMessage()]


def test_unregistered_event_logs_warning(session: Session, tenant, caplog) -> None:
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        created = dispatch(session, tenant.id, "unknown.event_code", title="测试标题", content="内容")

    assert created == 0
    warnings = _unregistered_warnings(caplog)
    assert len(warnings) == 1
    assert "unknown.event_code" in warnings[0]
    assert str(tenant.id) in warnings[0]
    assert "测试标题" in warnings[0]


def test_typo_and_case_variant_log_warning(session: Session, tenant, caplog) -> None:
    """事件码大小写/拼写变体（如 Alert、report.approve）同样属于未注册，会被告警"""
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        assert dispatch(session, tenant.id, "Alert", title="t", content="c") == 0
        assert dispatch(session, tenant.id, "report.approve", title="t", content="c") == 0
    assert len(_unregistered_warnings(caplog)) == 2


@pytest.mark.parametrize("event_code", ALL_REGISTERED)
def test_registered_event_never_warns_unregistered(
    session: Session, tenant, caplog, event_code: str
) -> None:
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        dispatch(session, tenant.id, event_code, title="t", content="c")
    assert _unregistered_warnings(caplog) == [], f"{event_code} 已注册，不应触发未注册告警"


def test_warning_does_not_raise_with_biz_params(session: Session, tenant, caplog) -> None:
    """告警不抛异常：业务调用方不应因未注册事件中断自身流程"""
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        created = dispatch(
            session,
            tenant.id,
            "not.registered.event",
            title="标题",
            content="内容",
            level="warn",
            biz_type="order",
            biz_id=1,
            payload={"k": "v"},
        )
    assert created == 0
    assert len(_unregistered_warnings(caplog)) == 1
