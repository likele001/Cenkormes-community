"""社区版默认权限与角色（不含 CRM、工资、财务、采购、仓储、AI 等 Pro 能力）。"""

DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    ("user.manage", "用户管理"),
    ("role.manage", "角色管理"),
    ("department.manage", "部门管理"),
    ("setting.manage", "系统设置"),
    ("notification.view", "消息通知"),
    ("dashboard.view", "看板查看"),
    ("attachment.view", "附件查看"),
    ("product.manage", "产品管理"),
    ("sku.manage", "产品型号管理"),
    ("process.manage", "工序管理"),
    ("order.manage", "订单管理"),
    ("work.manage", "工单管理"),
    ("task.manage", "任务管理"),
    ("dispatch.manage", "派工管理"),
    ("report.submit", "报工提交"),
    ("report.audit", "报工审核"),
    ("dict.manage", "字典管理"),
]

DEFAULT_ROLES: list[tuple[str, str]] = [
    ("admin", "管理员"),
    ("leader", "班组长"),
    ("employee", "员工"),
]

ROLE_PERMISSION_PRESETS: dict[str, set[str]] = {
    "admin": {code for code, _ in DEFAULT_PERMISSIONS},
    "leader": {
        "dispatch.manage", "report.audit", "report.submit",
        "order.manage", "work.manage", "task.manage",
        "notification.view", "dashboard.view",
    },
    "employee": {"report.submit", "notification.view"},
}

# 社区版硬限制（中间件 / 业务层可引用）
COMMUNITY_MAX_USERS = 5
COMMUNITY_MAX_SKUS = 20
COMMUNITY_MAX_PROCESSES = 10
COMMUNITY_MAX_ORDERS_PER_MONTH = 50
COMMUNITY_MAX_REPORTS_PER_MONTH = 500
