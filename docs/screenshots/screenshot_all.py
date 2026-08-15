"""LightMes 页面自动截图脚本（宣传用）
截取所有菜单页面 + 关键详情页
用法：python screenshot_all.py
"""

import asyncio
import json
import os
import re

from playwright.async_api import async_playwright

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(_CONFIG_PATH) as _f:
    _cfg = json.load(_f)

BASE_URL = _cfg.get("base_url", "https://admin.mes.cenkor.cn")
TENANT = _cfg["tenant"]
USERNAME = _cfg["username"]
PASSWORD = _cfg["password"]
SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))

def tenant_url(path):
    return f"{BASE_URL}/t/{TENANT}{path}"


# ========== 完整菜单页（从 AppMenu.vue 提取）==========
MENU_PAGES = [
    # 首页 & 仪表盘
    ("首页",                 "/home"),
    ("看板",                 "/dashboard/kanban"),
    ("大屏显示",              "/dashboard/screen"),

    # 数据中心
    ("报表总览",              "/reports"),
    ("采购统计",              "/reports/purchase"),

    # 智能中心
    ("智能帮助",              "/system/help"),
    ("AI深度分析",            "/system/ai-deep"),
    ("AI统计",               "/system/ai-stats"),
    ("自动化生产设置",         "/system/automation-settings"),

    # 系统 - 用户权限
    ("用户管理",              "/system/users"),
    ("邀请管理",              "/system/invites"),
    ("角色管理",              "/system/roles"),
    ("权限管理",              "/system/permissions"),

    # 系统 - 通知
    ("飞书通知",              "/system/feishu-notify"),
    ("企微通知",              "/system/wecom-notify"),
    ("钉钉通知",              "/system/dingtalk-notify"),
    ("消息中心",              "/system/message-center"),
    ("系统通知",              "/system/notifications"),

    # 系统 - 基础配置
    ("部门管理",              "/system/departments"),
    ("系统设置",              "/system/settings"),
    ("打印模板",              "/system/print-templates"),
    ("考勤记录",              "/system/attendance-records"),
    ("技能管理",              "/system/skills"),
    ("数据字典",              "/system/dictionary"),
    ("文件管理",              "/system/attachments"),
    ("操作日志",              "/system/operation-logs"),

    # 基础资料 - 产品物料
    ("产品管理",              "/master/products"),
    ("SKU管理",              "/master/skus"),
    ("SKU批量维护",          "/master/skus/batch"),
    ("供应商管理",            "/master/suppliers"),
    ("物料管理",              "/master/materials"),
    ("BOM管理",              "/master/boms"),

    # 基础资料 - 工序价格
    ("工序管理",              "/master/processes"),
    ("工艺路线",              "/master/process-routes"),
    ("工序工价",              "/master/process-prices"),

    # CRM
    ("客户管理",              "/production/customers"),
    ("商机管理",              "/crm/opportunities"),
    ("销售漏斗",              "/crm/pipeline"),
    ("公海池",                "/crm/public-pool"),
    ("商机统计",              "/crm/opportunity-stats"),
    ("客户标签",              "/crm/tags"),
    ("售后服务",              "/crm/after-sales"),
    ("CRM设置",              "/crm/settings"),

    # 生产 - 排程
    ("客户订单",              "/production/orders"),
    ("生产排程-工单",          "/production/work-orders"),
    ("生产计划",              "/plans"),
    ("生产任务",              "/production/tasks"),
    ("派工管理",              "/production/assignments"),
    ("排班管理",              "/production/shifts"),
    ("MRP运算",               "/mrp/runs"),
    ("报价管理",              "/quotations"),
    ("委外加工",              "/subcontract/orders"),

    # 生产 - 报工质检
    ("报工单位",              "/production/report-units"),
    ("报工管理",              "/production/reports"),
    ("工资核算",              "/production/salary"),
    ("工资条",                "/production/salary-slips"),
    ("溯源查询",              "/production/trace"),

    # 生产 - 仓库设备
    ("库存管理",              "/warehouse/stocks"),
    ("仓库管理",              "/warehouse/warehouses"),
    ("设备管理",              "/production/equipment"),

    # 采购
    ("采购单",                "/purchase/orders"),
    ("采购对账单",            "/purchase/statements"),

    # 财务
    ("客户对账单",            "/finance/statements"),
    ("流水账",                "/finance/ledgers"),
    ("利润表",                "/finance/profit"),

    # 时薪
    ("时薪管理",              "/production/hourly-salary"),
]

# ========== 详情/内页（有数据就截图）==========
DETAIL_PAGES = [
    ("采购单详情-1",           "/purchase/orders/1"),
    ("采购单详情-2",           "/purchase/orders/2"),
    ("采购对账单-新建",        "/purchase/statements/new"),
    ("客户订单详情-1",         "/production/orders/1"),
]

# ========== 合并 ==========
ALL_PAGES = [
    (f"{i:02d}-{title}", path)
    for i, (title, path) in enumerate(MENU_PAGES + DETAIL_PAGES, 1)
]


async def wait_page_loaded(page, timeout=15000):
    try:
        await page.wait_for_function(
            """() => {
                const el = document.querySelector('.app-main, .el-card, .el-table, .el-main, .admin-page');
                return el && el.offsetParent !== null;
            }""",
            timeout=timeout,
        )
    except:
        pass
    await page.wait_for_timeout(2000)


async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCREENSHOT_DIR, "tmp"), exist_ok=True)
    os.environ["TMPDIR"] = os.path.join(SCREENSHOT_DIR, "tmp")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        page = await context.new_page()

        # ── 登录 ──
        print("🔑 登录...")
        await page.goto(tenant_url("/login"), wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        result = await page.evaluate(
            f"""async () => {{
                try {{
                    const r = await fetch("{BASE_URL}/api/auth/login", {{
                        method: "POST", headers: {{"Content-Type": "application/json"}},
                        body: JSON.stringify({{tenant_code:"{TENANT}", username:"{USERNAME}", password:"{PASSWORD}", remember_me:true}})
                    }});
                    const d = await r.json();
                    if (r.ok && d?.data?.access_token) return 'OK:' + d.data.access_token;
                    return 'FAIL:' + JSON.stringify(d);
                }} catch(e) {{ return 'ERR:' + e.message; }}
            }}"""
        )
        if not result.startswith("OK:"):
            print(f"❌ 登录失败: {result}")
            await browser.close()
            return

        token = result[3:]
        print(f"  ✅ Token: {token[:20]}...")

        # ── 逐个截图 ──
        success = fail = skipped_rights = 0

        for filename, route_path in ALL_PAGES:
            target_url = tenant_url(route_path)
            filepath = os.path.join(SCREENSHOT_DIR, f"{filename}.png")

            try:
                print(f"📷 [{filename}] ", end="", flush=True)

                # 设置 token
                await page.evaluate(
                    f"""() => {{
                        localStorage.setItem('lightmes_admin_token', '{token}');
                        localStorage.setItem('lightmes_admin_token_storage_mode', 'local');
                        localStorage.setItem('lightmes_remember_login', '1');
                        sessionStorage.removeItem('lightmes_admin_token');
                    }}"""
                )

                await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                # 检查登录态
                if "/login" in page.url:
                    print("⟳ 重设token...", end=" ", flush=True)
                    await page.evaluate(
                        f"""() => {{
                            localStorage.setItem('lightmes_admin_token', '{token}');
                            localStorage.setItem('lightmes_admin_token_storage_mode', 'local');
                            localStorage.setItem('lightmes_remember_login', '1');
                            sessionStorage.removeItem('lightmes_admin_token');
                        }}"""
                    )
                    await page.reload(wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(5000)

                await wait_page_loaded(page)

                current = page.url
                redirected_home = "/home" in current and "/home" not in target_url and "dashboard" not in target_url

                await page.screenshot(path=filepath, full_page=True)
                size = os.path.getsize(filepath) // 1024

                if redirected_home:
                    print(f"↩️(首页) {size}K")
                    skipped_rights += 1
                else:
                    print(f"✅ {size}K")
                success += 1

            except Exception as e:
                print(f"❌ {e}")
                fail += 1

        await browser.close()

        total = len(ALL_PAGES)
        print(f"\n{'='*40}")
        print(f"🎉 完成！总 {total} 张")
        print(f"   ✅ 成功: {success}")
        print(f"   ↩️  无权限(跳首页): {skipped_rights}")
        print(f"   ❌ 失败: {fail}")
        print(f"📂 目录: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
