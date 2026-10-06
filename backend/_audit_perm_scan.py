"""审计脚本：扫描 admin/H5 API 的权限依赖覆盖情况（只读，不改动任何数据）。"""
import re
import pathlib
from collections import defaultdict

ROOT = pathlib.Path("/www/wwwroot/lightmes/backend/app")


def find_calls(txt: str, name: str):
    """括号配平提取 name( ... ) 的完整调用文本。"""
    out = []
    for m in re.finditer(re.escape(name) + r"\(", txt):
        i = m.end() - 1
        depth = 0
        for j in range(i, len(txt)):
            if txt[j] == "(":
                depth += 1
            elif txt[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append(txt[i : j + 1])
                    break
    return out


def main():
    # 1) 扫描 api 目录下所有 .py
    perm_used = defaultdict(list)  # code -> [file:line]
    login_only_files = []
    for f in sorted((ROOT / "api").rglob("*.py")):
        if "__pycache__" in str(f) or ".bak" in f.name:
            continue
        txt = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        # 收集权限码使用
        for call in find_calls(txt, "require_permissions") + find_calls(txt, "require_any_permissions"):
            for code in re.findall(r'"([a-z_]+(?:\.[a-z_]+)+)"', call):
                perm_used[code].append(rel)
        # 判断是否有 APIRouter 无依赖且文件内无任何 require_*
        has_perm = "require_permissions" in txt or "require_any_permissions" in txt
        routers = find_calls(txt, "APIRouter")
        ndep = [r for r in routers if "dependencies" not in r]
        if routers and ndep and not has_perm and "platform" not in rel:
            login_only_files.append((rel, len(ndep), len(routers)))

    print("== 仅登录、无任何权限依赖的文件（admin/h5/v1/ws）==")
    for rel, n, t in login_only_files:
        print(f"  {rel}  (无依赖router {n}/{t})")

    # 2) seed.py 中声明的权限码
    seed = (ROOT / "core" / "seed.py").read_text(encoding="utf-8")
    declared = set(re.findall(r'"([a-z_]+(?:\.[a-z_]+)+)"', seed))
    declared = {c for c in declared if "." in c and not c.startswith(("http", "app."))}

    used = set(perm_used.keys())
    # 过滤误报（形如 app.xxx / 版本号）
    used = {c for c in used if re.match(r"^[a-z_]+(\.[a-z_]+)+$", c) and not c.startswith(("app.", "sqlalchemy"))}

    print("\n== 声明但未被任何路由使用的权限码 ==")
    for c in sorted(declared - used):
        print(f"  {c}")

    print("\n== 路由使用但未在 seed 声明的权限码 ==")
    for c in sorted(used - declared):
        print(f"  {c}  <- {sorted(set(perm_used[c]))[:3]}")


if __name__ == "__main__":
    main()
