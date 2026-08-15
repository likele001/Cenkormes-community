"""LightMes 详情/内页截图脚本（宣传用）
截取所有新建、编辑、详情页
输出: D01-xxx.png ~ Dxx-xxx.png（不会覆盖已有菜单截图）
"""

import asyncio
import json
import os

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

# ========== 新建/编辑/详情页 ==========
# (显示名, 路由路径, 是否有数据标记)
DETAIL_PAGES = [
    # ── 新建表单 ──
    ("新建生产计划",         "/plans/new"),
    ("新建采购对账单",       "/purchase/statements/new"),
    ("客户订单导入",         "/production/orders/import"),

    # ── 有数据详情页 ──
    ("采购单详情-1",         "/purchase/orders/1"),
    ("采购单详情-2",         "/purchase/orders/2"),
    ("采购单详情-3",         "/purchase/orders/3"),
    ("采购对账单详情-1",     "/purchase/statements/1"),

    ("客户订单详情-1",       "/production/orders/1"),
    ("客户订单详情-2",       "/production/orders/2"),
    ("客户订单详情-3",       "/production/orders/3"),

    ("客户详情-1",           "/production/customers/1"),
    ("客户详情-2",           "/production/customers/2"),

    ("看板订单详情",         "/dashboard/kanban/orders/1"),

    # ── 个人/账户页面 ──
    ("个人资料",             "/account/profile"),
]

# 可能无数据但可以尝试的页面
TRY_PAGES = [
    ("MRP运算结果",          "/mrp/runs/1"),
    ("报价详情",             "/quotations/1"),
    ("委外详情",             "/subcontract/orders/1"),
    ("客户对账单详情",       "/finance/statements/1"),
]


def build_pages():
    """构建有序页面列表: 详情页 → 试页面"""
    result = []
    for i, (title, path) in enumerate(DETAIL_PAGES, 1):
        result.append((f"D{i:02d}-{title}", path, True))  # True = 有数据
    for i, (title, path) in enumerate(TRY_PAGES, len(DETAIL_PAGES) + 1):
        result.append((f"D{i:02d}-{title}", path, False))  # False = 无数据
    return result


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

    all_pages = build_pages()

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
        success = ok_home = fail = 0

        for filename, route_path, has_data in all_pages:
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
                redirected_home = "/home" in current and "/home" not in target_url

                await page.screenshot(path=filepath, full_page=True)
                size = os.path.getsize(filepath) // 1024

                if redirected_home:
                    if has_data:
                        print(f"⚠️(无数据→首页) {size}K")
                    else:
                        print(f"↩️(无权限/数据→首页) {size}K")
                    ok_home += 1
                else:
                    print(f"✅ {size}K")
                success += 1

            except Exception as e:
                print(f"❌ {e}")
                fail += 1

        await browser.close()

        total = len(all_pages)
        print(f"\n{'='*40}")
        print(f"🎉 完成！总 {total} 张")
        print(f"   ✅ 成功加载: {success - ok_home}")
        print(f"   ↩️  跳首页: {ok_home}")
        print(f"   ❌ 失败: {fail}")
        print(f"📂 目录: {SCREENSHOT_DIR}")
        print(f"💡 文件名 D01-xxx 开头的就是新截的详情页")


if __name__ == "__main__":
    asyncio.run(main())
