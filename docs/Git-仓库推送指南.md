# LightMes 仓库推送指南

> 三仓分工：私有开发仓改代码 → 导出 → 分别推社区版 / 专业版  
> 更新时间：2026-06-08

## 一、仓库一览

| 仓库 | 地址 | 可见性 | 本地目录 |
|------|------|--------|----------|
| 开发全集 | `git@github.com:likele001/lightmes.git` | 私有 | `/www/wwwroot/lightmes` |
| 社区版 | `git@github.com:likele001/lightmes-community.git` | **公开** | `/www/wwwroot/lightmes-community` |
| 专业版 | `git@github.com:likele001/lightmes-pro.git` | **私有** | `/www/wwwroot/lightmes-pro` |

**不要提交到开发仓的目录：** `community/`、`pro/`、`pro-build/`（已在 `.gitignore`）

---

## 二、一键发布社区版 + 专业版（推荐）

在**开发仓已提交并 push** 之后，一条命令完成拆分、导出、双仓推送：

```bash
cd /www/wwwroot/lightmes
bash scripts/release-all.sh "更新说明：例如修复 H5 报工、新增 CRM 字段"
```

试跑（只导出，不 commit / push）：

```bash
bash scripts/release-all.sh --dry-run "更新说明"
```

脚本会自动：

1. `split-packages.sh` + `verify-community-clean.sh`
2. 导出到 `/www/wwwroot/lightmes-community` 和 `/www/wwwroot/lightmes-pro`
3. 分别 `git add` → `commit` → `push` 到两个 GitHub 仓库

自定义本地目录（可选）：

```bash
COMMUNITY_DIR=/path/to/community PRO_DIR=/path/to/pro \
  bash scripts/release-all.sh "更新说明"
```

---

## 三、日常开发（私有 `lightmes`）

```bash
cd /www/wwwroot/lightmes

# 只提交源码与拆分工具，不提交生成物
git add backend/ frontend-admin-pro/ frontend-portal/ frontend-h5/
git add scripts/ docs/ README.md .gitignore
git status   # 确认没有 community/、pro/

git commit -m "feat: 你的改动说明"
git push origin main
```

---

## 四、推送社区版（公开，手动分步）

### 3.1 首次或更新

```bash
cd /www/wwwroot/lightmes

# 导出到独立目录（自动拆分、校验、剔除 AI 工具目录等杂项）
bash scripts/export-community-repo.sh
# 默认输出：/www/wwwroot/lightmes-community
```

### 3.2 首次初始化（仅第一次）

```bash
cd /www/wwwroot/lightmes-community
git init
git branch -M main
git remote add origin git@github.com:likele001/lightmes-community.git
git add .
git commit -m "$(cat <<'EOF'
初始发布：LightMes 社区版（扫码报工 + 审核）

面向中小型加工厂的轻量化 MES 社区版，包含订单、派工、
H5 扫码报工与两级审核。本仓库不含商业版源码。
EOF
)"
git push -u origin main
```

### 3.3 后续更新

```bash
cd /www/wwwroot/lightmes
bash scripts/export-community-repo.sh

cd /www/wwwroot/lightmes-community
git add .
git commit -m "更新社区版：写明本次改了什么"
git push origin main
```

> 导出脚本会**保留**已有 `.git`，无需每次 `git init`。

### 3.4 社区版自动剔除的内容

见 `scripts/community-export-excludes.txt`，主要包括：

- AI/IDE 目录：`.cursor/`、`.codebuddy/`、`.trae/` 等
- 内部文档：`CLAUDE.md`、竞品对比、`docs/OpenCore-版本规划.md`
- 临时文件：`song_output.*`、`skills-lock.json`
- 拆分工具：`split-packages.sh`、`pro-manifest.txt` 等

---

## 五、推送专业版（私有，手动分步）

### 4.1 导出

```bash
cd /www/wwwroot/lightmes
bash scripts/export-pro-repo.sh
# 默认输出：/www/wwwroot/lightmes-pro
```

### 4.2 首次初始化（仅第一次）

```bash
cd /www/wwwroot/lightmes-pro
git init
git branch -M main
git remote add origin git@github.com:likele001/lightmes-pro.git
git add .
git commit -m "$(cat <<'EOF'
初始发布：LightMes 专业版商业扩展包

在社区版基础上叠加算薪、CRM、财务、采购仓储、溯源、
看板及飞书/企微/小程序等集成能力。
EOF
)"
git push -u origin main
```

### 4.3 后续更新

```bash
cd /www/wwwroot/lightmes
bash scripts/export-pro-repo.sh

cd /www/wwwroot/lightmes-pro
git add .
git commit -m "更新专业版：写明本次改了什么"
git push origin main
```

### 4.4 专业版仓库结构

```
lightmes-pro/
├── overlay/              # 商业源码（叠加到社区版）
├── scripts/install.sh    # 安装脚本
├── LICENSE-COMMERCIAL.md
└── README.md
```

**务必保持 GitHub 仓库为 Private，不要公开。**

---

## 六、客户现场安装（社区 + Pro）

```bash
# 社区版（公开 clone）
git clone https://github.com/likele001/lightmes-community.git /www/wwwroot/lightmes
cd /www/wwwroot/lightmes/backend
cp env.example .env
pip install -r requirements.txt
alembic upgrade head

# 专业版（需仓库权限，私有 clone）
git clone git@github.com:likele001/lightmes-pro.git /www/wwwroot/lightmes-pro
bash /www/wwwroot/lightmes-pro/scripts/install.sh /www/wwwroot/lightmes

cd /www/wwwroot/lightmes/backend && alembic upgrade head
cd ../frontend-admin-pro && npm install && npm run build

# 验证
curl -s http://127.0.0.1:8000/api/health
# 应返回 "edition": "pro"
```

---

## 七、发版检查清单

```
[ ] 开发仓 lightmes 已提交并 push
[ ] bash scripts/export-community-repo.sh
[ ] 社区仓 commit + push（公开）
[ ] bash scripts/export-pro-repo.sh
[ ] 专业仓 commit + push（私有）
[ ] （可选）bash scripts/assemble-pro.sh 本地冒烟
```

---

## 八、常见问题

### Q：`git add` 提示 `community` 被 ignore？

你在**开发仓**里进了 `lightmes/community/`，这是生成目录，被 `.gitignore` 忽略是正常的。  
请到 `/www/wwwroot/lightmes-community` 操作，或先跑 `export-community-repo.sh`。

### Q：推送报 `Host key verification failed`？

```bash
mkdir -p ~/.ssh
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts
```

### Q：HTTPS 推送要用户名密码？

改用 SSH 地址：

```bash
git remote set-url origin git@github.com:likele001/lightmes-community.git
# 或
git remote set-url origin git@github.com:likele001/lightmes-pro.git
```

### Q：社区仓误推了 AI 工具目录？

已修复导出脚本。清理后重新推送：

```bash
bash scripts/export-community-repo.sh
cd /www/wwwroot/lightmes-community
git add -A
git commit -m "清理仓库：移除 AI 工具配置目录"
git push
```

### Q：Pro 能不能和 Community 放一个仓库？

不建议。社区版必须公开且**不能含 Pro 源码**；专业版必须私有。

---

## 九、命令速查

```bash
# 一键发布（最常用）
bash scripts/release-all.sh "更新说明"

# 拆分校验（开发仓内，不推送）
bash scripts/split-packages.sh
bash scripts/verify-community-clean.sh

# 单独导出
bash scripts/export-community-repo.sh      # → lightmes-community
bash scripts/export-pro-repo.sh            # → lightmes-pro

# 本地组装完整商业版（不提交）
bash scripts/assemble-pro.sh               # → pro-build/
```
