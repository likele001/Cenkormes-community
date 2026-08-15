# Git 双仓库发布（社区 / Pro 完全分开）

## 三个目录，三种角色

| 目录 | Git 仓库 | 可见性 | 说明 |
|------|----------|--------|------|
| **根目录 `lightmes/`** | 私有开发仓（可选） | 私有 | 日常开发全集，客户不拿这个 |
| **`lightmes-community/`** | 社区版仓 | **公开** | 只有扫码报工 + 审核，无商业源码 |
| **`lightmes-pro/`** | 商业版仓 | **私有** | 只有 `overlay/` + `install.sh`，叠到社区版上用 |

社区是社区，Pro 是 Pro，**两个 remote、两套权限，互不混提交。**

### 一键发布（推荐）

开发仓改完并 push 后，一条命令同步社区版 + 专业版：

```bash
cd /www/wwwroot/lightmes
bash scripts/release-all.sh "更新说明：例如修复报工审核"
```

详见 [Git-仓库推送指南.md](./Git-仓库推送指南.md)。

---

## 一、私有开发仓（你现在这个）

根目录继续改 `backend/`、`frontend-admin-pro/` 等，**不要**把 `community/`、`pro/` 提交进开发仓。

根目录 `.gitignore` 已忽略：

```
community/
pro/
pro-build/
```

开发仓只保留：

- 业务源码（`backend/`、`frontend-*`）
- 拆分工具（`scripts/community-patches/`、`scripts/pro-manifest.txt`、`scripts/split-packages.sh` 等）

```bash
cd /www/wwwroot/lightmes
git add backend/ frontend-admin-pro/ scripts/ docs/
git commit -m "feat: xxx"
git push origin main
```

---

## 二、导出并推送社区版（公开仓）

```bash
cd /www/wwwroot/lightmes

# 生成干净社区版目录（默认 ../lightmes-community）
bash scripts/export-community-repo.sh

cd ../lightmes-community
git init
git add .
git commit -m "release: lightmes community"

# 绑定公开仓库（示例）
git remote add origin https://github.com/你的账号/lightmes-community.git
git branch -M main
git push -u origin main
```

每次发社区版：先改开发仓 → 再跑 `export-community-repo.sh` → 在社区仓里 commit & push。

---

## 三、导出并推送商业版（私有仓）

```bash
cd /www/wwwroot/lightmes
bash scripts/export-pro-repo.sh

cd ../lightmes-pro
git init
git add .
git commit -m "release: lightmes pro"

git remote add origin https://github.com/你的账号/lightmes-pro.git
git branch -M main
git push -u origin main
```

**商业仓务必私有**，且不要和社区仓放在同一个公开仓库里。

---

## 四、客户现场怎么装

客户只拿两个包（或两个 git clone）：

```bash
git clone https://github.com/xxx/lightmes-community.git /www/wwwroot/lightmes
git clone git@github.com:xxx/lightmes-pro.git /www/wwwroot/lightmes-pro

bash /www/wwwroot/lightmes-pro/scripts/install.sh /www/wwwroot/lightmes
cd /www/wwwroot/lightmes/backend && alembic upgrade head
```

`GET /api/health` 应返回 `"edition": "pro"`。

---

## 五、发版检查清单

- [ ] 开发仓已提交并推送
- [ ] `bash scripts/export-community-repo.sh`
- [ ] `bash scripts/verify-community-clean.sh`（导出前自动执行）
- [ ] 社区仓 push（公开）
- [ ] `bash scripts/export-pro-repo.sh`
- [ ] 商业仓 push（私有）
- [ ] 用 `assemble-pro.sh` 或 install.sh 本地冒烟

---

## 六、常见问题

**Q：能不能一个仓库里用两个文件夹？**  
可以物理分目录，但开源时社区仓里绝不能出现 `pro/` 路径。双 remote 双仓库最干净。

**Q：`pro-build/` 要提交吗？**  
不要。本地临时组装，随时 `assemble-pro.sh` 重建。

**Q：社区仓里为什么还有 `scripts/start-celery.sh`？**  
社区版可跑基础服务；拆分/商业清单脚本已在导出时剔除。

**Q：`CLAUDE.md`、`song_output.*`、竞品对比文档要提交吗？**  
**不要**进 `lightmes-community`。导出脚本已自动剔除；协议说明看根目录 `LICENSE` 即可，README 不必重复写 AGPL 条款。
