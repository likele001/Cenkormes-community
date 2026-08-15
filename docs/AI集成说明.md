# LightMes AI 集成说明（M1 + 智能工厂 Phase A–D）

## 本次新增功能一览（相对纯 M1）

| 分类 | 功能 | 入口 | 权限 |
|------|------|------|------|
| **M1.5** | 预警阈值可配置 | 首页 AI 预警 → **阈值配置** | `ai.use` + `setting.manage` |
| **M1.5** | 审核批量 AI 摘要 | **件次报工审核** → **AI 批量摘要** | `ai.use` + `report.audit` |
| **M1.5** | 小程序排产建议只读 | 小程序管理端计划编辑 → **AI 排产建议**（LLM + OR-Tools Tab） | `ai.use` + `plan.manage` |
| **Phase E 小程序** | 员工 AI 检查一下 | 小程序逐件报工 → **AI 检查一下** | `ai.report_assist` |
| **Phase E 小程序** | 审核 AI / Vision | 小程序件次审核 → **AI 批量摘要** / **Vision 识图** | `ai.use` + `report.audit` |
| **Phase E 小程序** | 首页 AI 预警 | 小程序管理首页 → **AI 数据预警**、阈值 | `ai.alert.view` / `setting.manage` |
| **派工智能** | 工序绑定所需技能 | **基础数据 → 工序** 编辑页多选技能 | `process.manage` |
| **派工智能** | 自动派工按技能/车间/熟练度 | 生产计划 → 自动派工（逻辑增强，无新按钮名） | `plan.manage` 等 |
| **M2** | OR-Tools 约束排产 | 生产计划 → **智能排产** → Tab「OR-Tools 约束」 | `ai.use` + `plan.manage` |
| **M2** | Vision 审核识图 | 件次报工详情 → **Vision 识图辅助** | `ai.use` + `report.audit` |
| **M2 完整** | 租户独立 AI Key | **系统设置 → AI 网关** | `ai.use` + `setting.manage` |
| **M2 完整** | SSE 流式工厂助手 | PC 首页 → **工厂助手**（打字机效果） | `ai.use` |
| **M2 完整** | RAG 智能帮助 | **系统管理 → 智能帮助**；小程序「我的 → 智能帮助」 | 登录即可（H5）；PC 需 `ai.use` |
| **M2 完整** | 小程序工厂助手 | 小程序管理端「我的 → 工厂助手」 | `ai.use` |
| **深度 AI** | 因果/质量基因/工价/孪生/设备健康 | API `GET /admin/ai/deep/overview`（基础版） | `ai.use` |

**M1 原有功能（未删）：** 平台多网关、工厂助手、智能排产 LLM 建议、交期分析、H5 报工 AI 检查、首页 AI 预警卡片。

**2026-05-25 生产自动化（automation）：** 详见 **[LightMes生产自动化与智能中心操作手册.md](./LightMes生产自动化与智能中心操作手册.md)** 第四～十章。

| 能力 | API / 任务 |
|------|------------|
| 租户自动化配置 | `GET/PUT /admin/automation/settings` |
| 执行日志 / 预检 | `GET /admin/automation/logs`、`POST /admin/automation/dry-run` |
| 计划流水线 | Celery `production.automation.pipeline` |
| 每日简报 | `GET /admin/ai/brief`；Celery `ai.daily_brief.send`；推飞书/企微见 [工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md) |
| 审核预审 | Celery `audit.prescreen`；字段 `prescreen_level` |
| 交期/APS | `GET /admin/plans/{id}/forecast`、`/aps-strategy` |

完整业务流程见 **[AI智能工厂操作SOP.md](./AI智能工厂操作SOP.md)**。宝塔部署见 **[宝塔部署.md](./宝塔部署.md)**。

---

## 配置（平台总控）

1. 登录 **平台运营后台** → 菜单 **AI 模型**
2. 打开 **启用 AI（总开关）** 并保存
3. **新增网关**：每个网关独立配置 Base URL、API Key（OpenAI 兼容，含 OneAPI / DeepSeek 等）
4. 选中网关 → **管理模型**：在该网关下新增模型（编码在网关内唯一），**设默认模型**（全平台仅一个，业务调用使用该模型及其网关）
5. 可对单个网关点击 **测试** 验证连通；也可设 **默认网关**（无默认模型时的回退）

所有租户默认共用平台配置；租户可在 **系统设置 → AI 网关** 启用独立 Base URL / API Key（SaaS 自备密钥）。

## 租户功能（M1 原有 + 上表新增）

| 功能 | 权限 | 入口 |
|------|------|------|
| 老板问答 | `ai.use` | 管理端首页 → **工厂助手**（PC 支持 SSE 流式） |
| 智能帮助（RAG） | `ai.use`（PC）/ 登录（H5/小程序） | **系统管理 → 智能帮助**；小程序「我的 → 智能帮助」 |
| 租户 AI Key | `ai.use` + `setting.manage` | **系统设置 → AI 网关** |
| 数据预警 | `ai.alert.view` | 首页 **AI 数据预警**；Celery 8/12/16/20 点扫描；**阈值可配** |
| 智能排产（LLM + OR-Tools） | `ai.use` + `plan.manage` | 计划页 **智能排产**；可对比采纳 LLM 或 OR-Tools |
| 交期风险分析 | 同上 | 计划编辑页 → **AI 交期分析** |
| 报工 AI 检查 | `ai.report_assist` | H5 逐件报工 → **AI 检查一下** |
| 审核 AI 摘要 | `ai.use` + `report.audit` | 件次报工审核 → **AI 批量摘要**（PC + 小程序） |
| Vision 审核辅助 | `ai.use` + `report.audit` | 件次详情 → **Vision 识图辅助**（PC + 小程序） |
| 小程序 AI 检查 | `ai.report_assist` | 小程序逐件报工 → **AI 检查一下** |
| 小程序 AI 预警 | `ai.alert.view` | 小程序管理首页预警卡片 |
| 工序技能 → 自动派工 | `process.manage` / 派工权限 | 工序编辑绑技能；自动派工自动过滤 |

## 数据库迁移

```bash
cd backend
# 宝塔示例：
# /www/server/pyporject_evn/hightmes/bin/alembic upgrade head

# 若曾报 Can't locate revision '0037_order_opportunity_id'：
# 拉取最新代码（含 0037 补回文件）后再 upgrade head
```

迁移链：`0038_ai_platform.py` → `0039_ai_gateways.py` → `0040_process_skill_links.py`

## 部署闭环（Phase A）

详见 [AI智能工厂操作SOP.md](./AI智能工厂操作SOP.md)。

```bash
cd backend && alembic upgrade head
# 重启后端 + Celery worker/beat
cd ../frontend-admin-pro && npm run build
curl -s http://127.0.0.1:8000/api/health   # build 含 ai-factory
```

## Phase B 已交付

| 能力 | 说明 |
|------|------|
| 工序-技能绑定 | `PUT /admin/master/processes/{id}/skills`；自动派工按技能+车间过滤 |
| 审核 AI 摘要 | `POST /admin/ai/audit/summary`；件次报工审核页「AI 批量摘要」 |
| 预警阈值 | `GET/PUT /admin/ai/alert-settings`；首页预警卡片「阈值配置」 |

## Phase C 已交付

| 能力 | 说明 |
|------|------|
| OR-Tools 排产 | `POST /admin/ai/plan/{id}/schedule-optimize`；计划页 LLM / OR-Tools 对比采纳 |
| Vision 审核 | `POST /admin/ai/report-units/{id}/vision`；需平台 Vision 模型 |
| 派工熟练度 | 自动派工评分结合近 90 日报工统计 |

依赖：`pip install 'ortools>=9.8.0'`（未安装时优化器回退规则倒排）

## Phase D 基础版（规则/统计，可扩展 ML）

`GET /admin/ai/deep/overview` 及子路径：`causal`、`quality-genes`、`pricing`、`digital-twin`、`equipment-health`

## M2 已交付（完整）

| 能力 | 说明 |
|------|------|
| 租户 AI 网关 | `GET/PUT /admin/ai/gateway-settings`；覆盖平台 Key/Base URL/Model |
| SSE 流式对话 | `POST /admin/ai/chat/stream`；PC 工厂助手打字机 |
| RAG 帮助 | `POST /admin/ai/help`、`POST /h5/ai/help`；检索 `docs/*.md` |
| 小程序工厂助手 | `POST /h5/ai/chat`；管理端「我的 → 工厂助手」 |

## AI 修复补充（2026-05-25）

| 能力 | 说明 |
|------|------|
| Bug 修复 | `pricing_ai` SKU JOIN；RAG 路径/热刷新；SSE token 记录；审核摘要 0 条短路 |
| 深度分析页 | PC **系统管理 → AI 深度分析** |
| AI 统计 | **系统管理 → AI 调用统计**；`GET /admin/ai/stats` |
| 模型切换 | 工厂助手可选模型；`GET /admin/ai/models` |
| 自定义 prompt | **系统设置 → 工厂助手提示词** |
| 对话管理 | `GET/DELETE /admin/ai/conversations`；工厂助手历史删除 |
| H5 对齐 | 个人中心：智能帮助、工厂助手；首页 AI 预警（`ai.alert.view`） |
| 预警手动扫描 | PC/小程序首页 **立即扫描** / **扫描** |
| 小程序交期分析 | 计划编辑 → **AI交期分析** |

## 仍可选后续

- 强化学习排产、完整 YOLO/Prophet、AI 推荐调整员工技能（需管理员确认写库）

## 前端超时

管理端 AI 接口（智能排产、交期分析、工厂助手）HTTP 超时为 **120 秒**。若仍报 `timeout exceeded`，请重新 `npm run build` 管理端，并检查 Nginx `proxy_read_timeout` 不小于 120s。

## 依赖

```bash
pip install 'openai>=1.40.0'
```

## Celery

重启 worker 与 beat 后生效定时任务 `ai.alerts.scan`。

## 环境变量（可选，开发回退）

```env
AI_ENABLED=true
AI_BASE_URL=https://your-gateway/v1
AI_API_KEY=sk-xxx
AI_DEFAULT_MODEL=gpt-4o-mini
```

## 操作 SOP

完整流程见 [AI智能工厂操作SOP.md](./AI智能工厂操作SOP.md)。
