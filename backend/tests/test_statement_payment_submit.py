"""H5 客户回款登记改造（P1-7）回归测试

背景：H5 客户端可将 confirmed 对账单直接 mark-paid → 置 paid + 写收入
流水（created_by=客户），外部角色越权改账。

修复：改为「提交回款登记」——仅记录 payment_submitted_at/remark 并通知
财务核实；正式入账仍由管理端 mark-paid（财务操作）完成。

覆盖：
- 提交登记：状态仍 confirmed、无收入流水、登记落库（核心防回归）
- 旧路径 /mark-paid 兼容：行为同样只登记
- 重复提交：幂等更新、财务通知不重复
- draft/paid/他客户：400 或幂等返回
- 财务权限用户收到站内通知
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.h5 import customer as h5_customer_module
from app.core.deps import get_current_user, get_db
from app.crud.finance import create_statement, update_statement_status
from app.models.customer import Customer
from app.models.finance_ledger import FinanceLedger
from app.models.notification import Notification
from app.models.order import Order
from app.models.permission import Permission
from app.models.role import Role, role_permissions
from app.models.user import User, user_roles


def _mk_stmt(session, tenant_id, customer_id, code, status="confirmed"):
    """建一张对账单（含一笔订单明细），并按需置状态。"""
    order = Order(tenant_id=tenant_id, customer_id=customer_id, code=f"SO-{code}", status="confirmed")
    session.add(order)
    session.flush()
    stmt = create_statement(
        session,
        tenant_id=tenant_id,
        customer_id=customer_id,
        code=code,
        order_amounts=[(order.id, Decimal("100"))],
    )
    if status != "draft":
        update_statement_status(session, stmt, status)
    session.flush()
    return stmt


@pytest.fixture()
def cust_env(session, tenant, customer):
    """客户登录账号（关联档案）+ 财务账号（含 finance.manage 权限链路）。"""
    cu = User(tenant_id=tenant.id, username="cust1", password_hash="x", full_name="客户一号", is_active=True)
    session.add(cu)
    session.flush()
    customer.user_id = cu.id

    perm = Permission(code="finance.manage", name="财务管理")
    session.add(perm)
    session.flush()
    role = Role(tenant_id=tenant.id, code="fin_role", name="财务角色")
    session.add(role)
    session.flush()
    session.execute(role_permissions.insert().values(role_id=role.id, permission_id=perm.id))
    fin = User(tenant_id=tenant.id, username="fin1", password_hash="x", full_name="财务一号", is_active=True)
    session.add(fin)
    session.flush()
    session.execute(user_roles.insert().values(user_id=fin.id, role_id=role.id))
    session.flush()
    return cu, fin


@pytest.fixture()
def api(session, cust_env):
    cu, fin = cust_env
    app = FastAPI()
    app.include_router(h5_customer_module.router, prefix="/h5/customer")
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: cu
    return TestClient(app), fin


def _fin_notifications(session, fin_id) -> int:
    return int(
        session.scalar(
            select(func.count(Notification.id)).where(
                Notification.user_id == fin_id, Notification.title == "客户提交回款登记"
            )
        )
        or 0
    )


def test_submit_records_without_ledger(api, session, tenant, customer):
    """核心防回归：提交登记后状态仍 confirmed、无收入流水、登记时间落库。"""
    stmt = _mk_stmt(session, tenant.id, customer.id, "ST-PS-1")
    client, fin = api
    r = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit", params={"remark": "已转账 工行流水123"})
    assert r.status_code == 200, r.text
    session.refresh(stmt)
    assert stmt.status == "confirmed"  # 客户不能改账
    assert stmt.payment_submitted_at is not None
    assert stmt.payment_submitted_remark == "已转账 工行流水123"
    ledgers = session.scalars(select(FinanceLedger).where(FinanceLedger.statement_id == stmt.id)).all()
    assert ledgers == []
    assert _fin_notifications(session, fin.id) == 1


def test_legacy_mark_paid_path_compatible(api, session, tenant, customer):
    """旧版客户端调用 /mark-paid 时行为同样只登记（兼容不破）。"""
    stmt = _mk_stmt(session, tenant.id, customer.id, "ST-PS-2")
    client, _ = api
    r = client.post(f"/h5/customer/statements/{stmt.id}/mark-paid")
    assert r.status_code == 200, r.text
    session.refresh(stmt)
    assert stmt.status == "confirmed"
    assert stmt.payment_submitted_at is not None
    assert session.scalars(select(FinanceLedger).where(FinanceLedger.statement_id == stmt.id)).all() == []


def test_duplicate_submit_updates_but_notifies_once(api, session, tenant, customer):
    """重复提交：备注更新、登记时间刷新、财务通知不重复。"""
    stmt = _mk_stmt(session, tenant.id, customer.id, "ST-PS-3")
    client, fin = api
    r1 = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit", params={"remark": "第一次"})
    assert r1.status_code == 200, r1.text
    r2 = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit", params={"remark": "第二次 流水456"})
    assert r2.status_code == 200, r2.text
    session.refresh(stmt)
    assert stmt.payment_submitted_remark == "第二次 流水456"
    assert _fin_notifications(session, fin.id) == 1


def test_draft_rejected(api, session, tenant, customer):
    """未确认（draft）对账单不可提交登记。"""
    stmt = _mk_stmt(session, tenant.id, customer.id, "ST-PS-4", status="draft")
    client, _ = api
    r = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit")
    assert r.status_code == 400


def test_paid_statement_noop(api, session, tenant, customer):
    """财务已入账（paid）后提交 → 幂等返回，不写登记。"""
    stmt = _mk_stmt(session, tenant.id, customer.id, "ST-PS-5", status="paid")
    client, _ = api
    r = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit")
    assert r.status_code == 200
    session.refresh(stmt)
    assert stmt.payment_submitted_at is None  # paid 无需登记
    assert stmt.status == "paid"


def test_other_customer_statement_rejected(api, session, tenant, customer):
    """他客户的对账单不可提交（归属校验）。"""
    other_c = Customer(tenant_id=tenant.id, code="C-OTH-PS", name="别家客户", is_active=True)
    session.add(other_c)
    session.flush()
    stmt = _mk_stmt(session, tenant.id, other_c.id, "ST-PS-6")
    client, _ = api
    r = client.post(f"/h5/customer/statements/{stmt.id}/payment-submit")
    assert r.status_code == 400
