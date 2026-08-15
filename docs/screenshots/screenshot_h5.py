"""LightMes H5 员工端页面截图脚本（宣传用）
针对移动端 H5 员工报工场景
- 站点: https://mes.cenkor.cn/
- 租户: DEMO
- 账号: lsj5492 (员工)
- 输出文件名: H5-xxx.png
- 视口: 移动端尺寸 (iPhone 14 Pro)
"""

import asyncio
import json
import os

from playwright.async_api import async_playwright

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_h5.json")
with open(_CONFIG_PATH) as _f:
    _cfg = json.load(_f)

BASE_URL = _cfg.get("base_url", "https://mes.cenkor.cn")
TENANT = _cfg["tenant"]
USERNAME = _cfg["username"]
PASSWORD = _cfg["password"]
SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))


def h5_path(route_path):
    """H5 使用 hash 路由: /#/t/{tenant}/xxx"""
    return f"{BASE_URL}/#/t/{TENANT}{route_path}"


# ========== H5 员工端核心页面（来自 frontend-h5/src/router/index.ts）==========
H5_PAGES = [
    # ── 登录页（公开展示） ──
    ("登录页",               "/login"),

    # ── 首页/导航 ──
    ("首页",                 "/home"),
    ("生产看板",             "/screen"),

    # ── 任务列表/详情（核心） ──
    ("我的任务",             "/tasks"),
    ("任务详情-1",           "/tasks/47"),  # lsj5492 分配的任务
    ("任务详情-2",           "/tasks/46"),
    ("任务详情-3",           "/tasks/56"),

    # ── 报工核心功能 ──
    ("扫码报工",             "/report"),
    ("逐件报工",             "/report-unit"),
    ("主动报工-输入任务码",  "/report-manual"),
    ("报工记录",             "/report-history"),

    # ── 考勤 ──
    ("考勤打卡",             "/attendance"),

    # ── 工资 ──
    ("我的工资",             "/wages"),
    ("电子工资条",           "/salary/slip"),

    # ── 消息/账户 ──
    ("消息中心",             "/notifications"),
    ("个人资料",             "/profile"),
    ("智能帮助",             "/help"),
    ("智能中心",             "/ai-hub"),
]


async def wait_page_loaded(page, timeout=15000):
    try:
        await page.wait_for_function(
            """() => {
                const el = document.querySelector(
                    '.van-page, .van-tabs, .van-cell, .van-button, .van-list, .van-nav-bar, .main-content, main, [class*=page]'
                );
                return el && el.offsetParent !== null;
            }""",
            timeout=timeout,
        )
    except:
        pass
    await page.wait_for_timeout(2500)


async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCREENSHOT_DIR, "tmp"), exist_ok=True)
    os.environ["TMPDIR"] = os.path.join(SCREENSHOT_DIR, "tmp")

    async with async_playwright() as p:
        # 移动端视口
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},  # iPhone 14 Pro
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            locale="zh-CN",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        )
        page = await context.new_page()

        # ── 1. 打开登录页（建立页面上下文） ──
        print("🔑 打开登录页...")
        await page.goto(f"{BASE_URL}/#/t/{TENANT}/login", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # ── 2. 通过 API 登录获取 token ──
        print("🔑 通过 API 登录...")
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

        # ── 3. 设置 H5 token（lightmes_token） ──
        await page.evaluate(
            f"""() => {{
                localStorage.setItem('lightmes_token', '{token}');
                localStorage.setItem('lightmes_token_storage_mode', 'local');
                localStorage.setItem('lightmes_remember_login', '1');
                sessionStorage.removeItem('lightmes_token');
            }}"""
        )
        print("  ✅ H5 token 已设置")

        # ── 4. 逐个截图 ──
        success = fail = 0

        for i, (title, route_path) in enumerate(H5_PAGES, 1):
            filename = f"H5-{i:02d}-{title}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            target_url = h5_path(route_path)

            try:
                print(f"📷 [{filename}] ", end="", flush=True)

                # 设置 token（每页都设置一次，确保不丢）
                await page.evaluate(
                    f"""() => {{
                        localStorage.setItem('lightmes_token', '{token}');
                        localStorage.setItem('lightmes_token_storage_mode', 'local');
                        localStorage.setItem('lightmes_remember_login', '1');
                        sessionStorage.removeItem('lightmes_token');
                    }}"""
                )

                await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                # 检查登录态
                if "/login" in page.url and route_path != "/login":
                    print("⟳ 重设token...", end=" ", flush=True)
                    await page.evaluate(
                        f"""() => {{
                            localStorage.setItem('lightmes_token', '{token}');
                            localStorage.setItem('lightmes_token_storage_mode', 'local');
                            localStorage.setItem('lightmes_remember_login', '1');
                            sessionStorage.removeItem('lightmes_token');
                        }}"""
                    )
                    await page.reload(wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(5000)

                await wait_page_loaded(page)

                await page.screenshot(path=filepath, full_page=True)
                size = os.path.getsize(filepath) // 1024
                print(f"✅ {size}K")
                success += 1

            except Exception as e:
                print(f"❌ {e}")
                fail += 1

        await browser.close()

        total = len(H5_PAGES)
        print(f"\n{'='*40}")
        print(f"🎉 H5 截图完成！")
        print(f"   总: {total}  ✅ 成功: {success}  ❌ 失败: {fail}")
        print(f"📂 目录: {SCREENSHOT_DIR}")
        print(f"💡 文件名 H5-xxx.png 是新截的移动端截图")


if __name__ == "__main__":
    asyncio.run(main())
