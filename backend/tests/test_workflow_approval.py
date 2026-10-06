"""工作流审批权限修复（P0-1）回归测试

覆盖：
- check_available_approver：无角色拒绝 / 角色匹配放行 / admin、superuser 兜底 / 跨租户拒绝
- approve_task：权限拦截与正常推进
- transfer_task：无权限拒绝 / 跨租户目标拒绝 / 合法转交后仅目标可审批
- list_todo：未指派任务按角色过滤（admin 可见全部）
"""
from __future__ import annotations

import pytest

from app.models.role import Role
from app.models.tenant import Tenant
from app.models.user import User, user_roles
from app.models.workflow import ApprovalInstance, ApprovalTask
from app.services.workflow import engine as svc
from app.services.workflow.engine import WorkflowError
from app.services.workflow.task import check_available_approver, list_todo


def _mk_role(db, tenant: Tenant, code: str) -> Role:
    r = Role(tenant_id=tenant.id, code=code, name=code)
    db.add(r)
    db.flush()
    return r


def _mk_user(db, tenant: Tenant, username: str, role_ids=(), is_superuser: bool = False) -> User:
    u = User(
        tenant_id=tenant.id,
        username=username,
        password_hash="x",
        is_active=True,
        is_superuser=is_superuser,
    )
    db.add(u)
    db.flush()
    for rid in role_ids:
        db.execute(user_roles.insert().values(user_id=u.id, role_id=rid))
    db.flush()
    return u


def _mk_instance(db, tenant: Tenant, initiator: User, biz_type: str = "order") -> ApprovalInstance:
    inst = ApprovalInstance(
        tenant_id=tenant.id,
        flow_version=1,
        biz_type=biz_type,
        biz_id=1,
        status="running",
        initiator_id=initiator.id,
        current_node="step_1",
    )
    db.add(inst)
    db.flush()
    return inst


def _mk_task(db, tenant: Tenant, inst: ApprovalInstance, role: str = "manager",
             assignee_id=None) -> ApprovalTask:
    t = ApprovalTask(
        tenant_id=tenant.id,
        instance_id=inst.id,
        step_order=1,
        node_key="step_1",
        node_type="userTask",
        approver_role=role,
        assignee_id=assignee_id,
        sign_mode="single",
        status="pending",
    )
    db.add(t)
    db.flush()
    return t


def test_unassigned_task_requires_role(session, tenant, admin_role):
    """未指派任务：无角色拒绝、角色匹配放行、admin 兜底放行。"""
    manager_role = _mk_role(session, tenant, "manager")
    outsider = _mk_user(session, tenant, "u1")
    manager = _mk_user(session, tenant, "u2", [manager_role.id])
    admin_user = _mk_user(session, tenant, "u3", [admin_role.id])
    initiator = _mk_user(session, tenant, "u4")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst)

    assert check_available_approver(session, task, outsider.id) is False
    assert check_available_approver(session, task, manager.id) is True
    assert check_available_approver(session, task, admin_user.id) is True


def test_cross_tenant_user_rejected(session, tenant):
    """跨租户用户（即使同名角色）不能审批本租户任务。"""
    other = Tenant(code="OTHER", name="他厂")
    session.add(other)
    session.flush()
    other_role = _mk_role(session, other, "manager")
    other_user = _mk_user(session, other, "ou", [other_role.id])
    initiator = _mk_user(session, tenant, "iu")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst)

    assert check_available_approver(session, task, other_user.id) is False


def test_assignee_task_only_assignee(session, tenant, admin_role):
    """已指派任务：仅 assignee 可审批（admin 也不放行）。"""
    manager_role = _mk_role(session, tenant, "manager")
    a = _mk_user(session, tenant, "a", [manager_role.id])
    b = _mk_user(session, tenant, "b", [manager_role.id])
    admin_user = _mk_user(session, tenant, "adm2", [admin_role.id])
    initiator = _mk_user(session, tenant, "i2")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst, assignee_id=a.id)

    assert check_available_approver(session, task, a.id) is True
    assert check_available_approver(session, task, b.id) is False
    assert check_available_approver(session, task, admin_user.id) is False


def test_approve_task_permission_enforced(session, tenant):
    """approve_task：无角色被拒；角色用户审批后流程走完。"""
    manager_role = _mk_role(session, tenant, "manager")
    manager = _mk_user(session, tenant, "m2", [manager_role.id])
    outsider = _mk_user(session, tenant, "o2")
    initiator = _mk_user(session, tenant, "i4")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst, role="manager")

    with pytest.raises(WorkflowError):
        svc.approve_task(session, task.id, operator_id=outsider.id)

    t = svc.approve_task(session, task.id, operator_id=manager.id)
    assert t.status == "approved"
    session.refresh(inst)
    assert inst.status == "approved"


def test_transfer_requires_permission_and_tenant(session, tenant):
    """转交：无权限拒绝、跨租户目标拒绝、合法转交后仅目标可审批。"""
    manager_role = _mk_role(session, tenant, "manager")
    approver = _mk_user(session, tenant, "ap", [manager_role.id])
    target = _mk_user(session, tenant, "tg", [manager_role.id])
    outsider = _mk_user(session, tenant, "os")
    initiator = _mk_user(session, tenant, "i3")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst)

    with pytest.raises(WorkflowError):
        svc.transfer_task(session, task.id, operator_id=outsider.id, to_user_id=target.id)

    other = Tenant(code="OTHER2", name="他厂2")
    session.add(other)
    session.flush()
    other_user = _mk_user(session, other, "ou2")
    with pytest.raises(WorkflowError):
        svc.transfer_task(session, task.id, operator_id=approver.id, to_user_id=other_user.id)

    with pytest.raises(WorkflowError):
        svc.transfer_task(session, task.id, operator_id=approver.id, to_user_id=approver.id)

    t = svc.transfer_task(session, task.id, operator_id=approver.id, to_user_id=target.id)
    assert t.assignee_id == target.id
    assert check_available_approver(session, t, target.id) is True
    assert check_available_approver(session, t, approver.id) is False


def test_list_todo_filters_unassigned_by_role(session, tenant, admin_role):
    """list_todo：未指派任务仅对该角色可见；admin 可见全部；无角色不可见。"""
    manager_role = _mk_role(session, tenant, "manager")
    manager = _mk_user(session, tenant, "m1", [manager_role.id])
    outsider = _mk_user(session, tenant, "o9")
    admin_user = _mk_user(session, tenant, "ad9", [admin_role.id])
    initiator = _mk_user(session, tenant, "i9")
    inst = _mk_instance(session, tenant, initiator)
    task = _mk_task(session, tenant, inst, role="manager")

    mgr_ids = [x.id for x in list_todo(session, tenant.id, manager.id)]
    out_ids = [x.id for x in list_todo(session, tenant.id, outsider.id)]
    adm_ids = [x.id for x in list_todo(session, tenant.id, admin_user.id)]

    assert task.id in mgr_ids
    assert task.id not in out_ids
    assert task.id in adm_ids
