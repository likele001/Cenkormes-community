"""工资条签收快照锁定（P1-11）回归测试

背景：`ensure_salary_slip` 每次调用都用报工/补贴数据重算并覆盖工资条金额。
员工签名确认的是签名时刻的金额，签名后补录报工/调整补贴会把「已签名的金额」
改掉——签收快照失效（审计 Part：`crud/salary_slip.py:77-97`）。

修复：
- 新增 `is_slip_amount_locked`：已签收（signed_at / confirm_status=signed）
  或已发放（paid_at）→ 金额锁定
- `ensure_salary_slip` 锁定后直接返回，不重算不覆盖
- 管理员重置签收（reset）解除签收锁定；发放锁定不因重置解除（保护 ledger 一致性）

覆盖：
- 未签名：金额随报工数据正常重算（防回归）
- 已签名：补录报工后金额不变（快照锁定）
- 已发放：补录报工后金额不变（账实一致）
- 已拒签：允许重算（异议处理路径）
- 签名 → 重置 → 重新可算
- 已发放 → 重置 → 仍锁定
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from app.crud.salary_slip import ensure_salary_slip, is_slip_amount_locked, reset_salary_slip_confirm
from app.models.salary import SalaryItem
from app.models.user import User


MONTH = "2026-09"


@pytest.fixture()
def emp(session, tenant) -> User:
    u = User(tenant_id=tenant.id, username="emp_lock", password_hash="x", full_name="李四", is_active=True)
    session.add(u)
    session.flush()
    return u


def _mk_item(session, tenant_id, user_id, amount="100", month=MONTH):
    """造一条计件报工工资明细（report_id 为空，绕过单号唯一约束）。"""
    it = SalaryItem(
        tenant_id=tenant_id,
        user_id=user_id,
        unit_price=Decimal("1"),
        good_qty=1,
        amount=Decimal(amount),
        item_type="piece",
        month=month,
    )
    session.add(it)
    session.flush()
    return it


def _net(session, tenant_id, user_id, month=MONTH) -> float:
    slip = ensure_salary_slip(session, tenant_id=tenant_id, user_id=user_id, month=month)
    return float(slip.net_amount)


def test_pending_slip_recalculates(session, tenant, emp):
    """未签名：金额随报工数据正常重算（防回归）。"""
    _mk_item(session, tenant.id, emp.id, amount="100")
    assert _net(session, tenant.id, emp.id) == 100.0
    _mk_item(session, tenant.id, emp.id, amount="50")
    assert _net(session, tenant.id, emp.id) == 150.0


def test_signed_slip_not_overwritten(session, tenant, emp):
    """已签名：签名后补录报工，金额保持签名快照不变。"""
    _mk_item(session, tenant.id, emp.id, amount="100")
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert float(slip.net_amount) == 100.0
    slip.signed_at = datetime.now()
    slip.confirm_status = "signed"
    session.flush()

    _mk_item(session, tenant.id, emp.id, amount="50")  # 签名后补录
    slip2 = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert slip2.id == slip.id
    assert float(slip2.net_amount) == 100.0  # 快照锁定


def test_paid_slip_not_overwritten(session, tenant, emp):
    """已发放：金额锁定，保证发放流水与工资条一致。"""
    _mk_item(session, tenant.id, emp.id, amount="200")
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    slip.pay_status = "paid"
    slip.paid_at = datetime.now()
    session.flush()

    _mk_item(session, tenant.id, emp.id, amount="80")
    slip2 = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert float(slip2.net_amount) == 200.0


def test_rejected_slip_recalculates(session, tenant, emp):
    """已拒签（未签名）：允许重算（管理员按异议修正后重新查看/签名）。"""
    _mk_item(session, tenant.id, emp.id, amount="100")
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    slip.confirm_status = "rejected"
    slip.reject_reason = "金额不对"
    slip.rejected_at = datetime.now()
    session.flush()

    _mk_item(session, tenant.id, emp.id, amount="50")  # 修正补差
    slip2 = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert float(slip2.net_amount) == 150.0


def test_reset_unlocks_signed_slip(session, tenant, emp):
    """签名 → 管理员重置 → 解锁可重算。"""
    _mk_item(session, tenant.id, emp.id, amount="100")
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    slip.signed_at = datetime.now()
    slip.confirm_status = "signed"
    session.flush()

    _mk_item(session, tenant.id, emp.id, amount="50")
    reset_salary_slip_confirm(session, tenant_id=tenant.id, slip_id=slip.id)
    assert is_slip_amount_locked(slip) is False
    slip2 = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert float(slip2.net_amount) == 150.0


def test_paid_lock_survives_reset(session, tenant, emp):
    """已发放 → 重置签收后金额仍锁定（保护 ledger 一致性）。"""
    _mk_item(session, tenant.id, emp.id, amount="300")
    slip = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    slip.pay_status = "paid"
    slip.paid_at = datetime.now()
    session.flush()

    _mk_item(session, tenant.id, emp.id, amount="90")
    reset_salary_slip_confirm(session, tenant_id=tenant.id, slip_id=slip.id)
    assert is_slip_amount_locked(slip) is True
    slip2 = ensure_salary_slip(session, tenant_id=tenant.id, user_id=emp.id, month=MONTH)
    assert float(slip2.net_amount) == 300.0
