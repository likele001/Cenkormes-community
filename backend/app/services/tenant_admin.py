"""新建租户时初始化管理员账号的默认显示名。"""

DEFAULT_ADMIN_FULL_NAME = "系统管理员"


def resolve_admin_full_name(tenant_name: str, admin_full_name: str | None = None) -> str:
    name = (admin_full_name or "").strip()
    if name:
        return name
    tn = (tenant_name or "").strip()
    if tn:
        return f"{tn}管理员"
    return DEFAULT_ADMIN_FULL_NAME
