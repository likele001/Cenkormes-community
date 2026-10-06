# -*- coding: utf-8 -*-
"""套餐授权网关：Pro 专属功能按租户套餐层级拦截（SaaS 付费墙）。

改造说明：
- 保留原有 Pro 专属路由拦截逻辑（PRO_ONLY_ROUTES）。
- 新增「试用基础版」档位（starter 套餐，交付模式 saas）：对该档位租户，
  命中 STARTER_TRIAL_DENIED 高级模块前缀的接口一律拦截，其余接口放行。
  这样可安全地只开放「生产闭环 + 报工 + 自动计件工资 + 客户自助下单」，
  并把 AI 智能化、多 IM 推送（飞书/企微/钉钉）、财务/仓库/设备/MRP/采购、
  平台/支付 等高级能力闸住；不会影响现有 community/pro/enterprise 档位。
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.db import SessionLocal
from app.core.response import fail
from app.core.security import decode_token
from app.models.saas_package import PACKAGE_TIER_STARTER, SaasPackage
from app.models.tenant import Tenant

logger = logging.getLogger("uvicorn.error")

# Pro 专属路由前缀（与 scripts/pro-manifest.txt 对齐）
PRO_ONLY_ROUTES = (
    "/api/admin/trace",
    "/api/admin/finance",
    "/api/admin/warehouse",
    "/api/admin/equipment",
    "/api/admin/reports",
    "/api/admin/ai",
    "/api/admin/ai-employees",
    "/api/admin/automation",
    "/api/admin/purchase",
    "/api/admin/shift",
    "/api/admin/mrp",
    "/api/admin/quotation",
    "/api/admin/subcontract",
    "/api/admin/mold",
    "/api/admin/spc",
    "/api/admin/approval",
    "/api/admin/exec-dashboard",
    "/api/admin/industry",
    "/api/admin/production/crm",
    "/api/admin/production/customers",
    "/api/admin/system/feishu",
    "/api/admin/system/wecom",
    "/api/admin/system/dingtalk",
    "/api/admin/system/wechat-miniapp",
    "/api/admin/system/attendance-records",
    "/api/admin/system/message-center",
    "/api/admin/system/print-templates",
    "/api/admin/system/operation-logs",
    "/api/admin/system/skills",
    "/api/h5/ai",
    "/api/h5/ai-employees",
    "/api/h5/customer",
    "/api/h5/salary",
    "/api/h5/attendance",
)

# 允许访问 Pro 功能的套餐层级（pro 专业版 / enterprise 企业版）
ALLOWED_TIERS = {"pro", "enterprise"}

# 免检租户白名单（一般无需配置，测试租户直接给 enterprise 套餐）
WHITELIST_TENANT_IDS: set[int] = set()

# ============================================================================
# 试用基础版（starter / saas 交付）黑名单：命中即拦截，其余全部放行。
# 用于「先拿第一个真实付费客户」的最小试用档位：只开放核心生产闭环。
# ============================================================================
STARTER_TRIAL_DENIED = (
    # 高级业务模块
    "/api/admin/finance",
    "/api/admin/warehouse",
    "/api/admin/equipment",
    "/api/admin/trace",
    "/api/admin/reports",
    "/api/admin/purchase",
    "/api/admin/mrp",
    "/api/admin/erp",
    "/api/admin/quotation",
    "/api/admin/subcontract",
    "/api/admin/mold",
    "/api/admin/spc",
    "/api/admin/approval",
    "/api/admin/workflow",
    "/api/admin/exec-dashboard",
    "/api/admin/automation",
    "/api/admin/shift",
    "/api/admin/industry",
    # AI 智能化
    "/api/admin/ai",
    "/api/admin/assistant",
    "/api/h5/ai",
    # 多 IM 推送（飞书 / 企微 / 钉钉 / 微信小程序推送配置）
    "/api/admin/system/feishu",
    "/api/admin/system/wecom",
    "/api/admin/system/dingtalk",
    "/api/admin/system/wechat-miniapp",
    "/api/admin/system/message-center",
    "/api/h5/feishu",
    "/api/h5/wecom",
    "/api/h5/dingtalk",
    "/api/feishu",
    "/api/wecom",
    "/api/dingtalk",
    # 平台运营 / 支付
    "/api/platform",
    "/api/payment",
    "/api/admin/push-monitor",
)


def _path_hits(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(p) for p in prefixes)


class PackageGateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        auth = request.headers.get("authorization", "")

        tenant_id = 0
        tier = None
        if not auth.lower().startswith("bearer "):
            pass
        else:
            token = auth.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)
                tenant_id = int(payload.get("tenant_id") or 0)
            except Exception:
                tenant_id = 0

        if tenant_id and tenant_id not in WHITELIST_TENANT_IDS:
            db = SessionLocal()
            try:
                tenant = db.get(Tenant, tenant_id)
                if tenant and tenant.current_package_id:
                    pkg = db.get(SaasPackage, tenant.current_package_id)
                    tier = pkg.tier if pkg else None
            finally:
                db.close()

        # 试用基础版：黑名单拦截，其余放行（不影响无 token / 免检租户）
        if tier == PACKAGE_TIER_STARTER:
            if _path_hits(path, STARTER_TRIAL_DENIED):
                return JSONResponse(
                    status_code=200,
                    content=fail(403, "当前套餐不含此功能，请升级后使用"),
                )
            return await call_next(request)

        # 原 Pro 专属逻辑
        if not path.startswith("/api"):
            return await call_next(request)
        if not _path_hits(path, PRO_ONLY_ROUTES):
            return await call_next(request)

        if not auth.lower().startswith("bearer "):
            return await call_next(request)

        if tenant_id and tenant_id in WHITELIST_TENANT_IDS:
            return await call_next(request)

        if tier not in ALLOWED_TIERS:
            return JSONResponse(
                status_code=200,
                content=fail(403, "当前套餐不含此功能，请升级 Pro 专业版"),
            )
        return await call_next(request)


# ==============================
# 试用基础版(starter) 对前端下发的「被禁模块」清单
# 前端菜单据此隐藏对应分组（finance/erp/purchase/ai/warehouse等）。
# 仅对 starter 档位生效；其余档位返回空列表。
# ==============================
STARTER_BLOCKED_MODULES = [
    "finance", "erp", "purchase", "warehouse", "crm",
    "equipment", "trace", "shift", "ai", "mrp", "quotation",
    "subcontract", "mold", "spc", "approval", "workflow",
    "exec_dashboard", "automation", "industry", "im",
    "message_center", "print_templates", "skills",
    "attendance", "operation_log",
]


def get_tenant_blocked_modules(db, tenant_id: int) -> list[str]:
    """若租户套餐为 starter(试用基础版)，返回被禁模块清单，否则空。"""
    tenant = db.get(Tenant, tenant_id)
    tier = None
    if tenant and tenant.current_package_id:
        pkg = db.get(SaasPackage, tenant.current_package_id)
        tier = pkg.tier if pkg else None
    if tier == PACKAGE_TIER_STARTER:
        return list(STARTER_BLOCKED_MODULES)
    return []
