"""区分管理后台入口与 H5 入口的账号能力。"""

from app.models.user import User

# 仅允许使用手机 H5 的角色；不含 admin / leader / qc 等管理类角色
H5_PORTAL_ROLE_CODES = frozenset({"employee", "customer"})

ADMIN_PORTAL_HEADER = "X-LightMes-Portal"
ADMIN_PORTAL_VALUE = "admin"


def user_role_codes(user: User) -> set[str]:
    return {r.code for r in (user.roles or [])}


def is_h5_portal_user(user: User) -> bool:
    """纯员工/客户账号，禁止进入 PC 管理后台。"""
    if user.is_superuser:
        return False
    roles = user_role_codes(user)
    if not roles:
        return True
    return roles.issubset(H5_PORTAL_ROLE_CODES)


def assert_admin_portal_user(user: User) -> None:
    from fastapi import HTTPException

    if is_h5_portal_user(user):
        roles = sorted(user_role_codes(user))
        if "customer" in roles:
            raise HTTPException(status_code=403, detail="客户账号请使用手机端 H5 登录")
        raise HTTPException(status_code=403, detail="员工账号请使用手机端 H5 报工，不能访问管理后台")
