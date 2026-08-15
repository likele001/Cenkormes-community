# LightMes 生产自动化与智能中心操作手册

> 版本：`manual-20260525-v1` · 适用：PC 管理端、员工 H5、微信小程序管理端  
> 部署 build 标记：`20260525-automation`

本文档为 **生产自动化 + 智能中心** 的总入口。专题文档见 [附录 C](#附录-c-文档索引)。

---

## 一、产品说明

### 1.1 定位

LightMes 面向 **计件加工厂** 的轻量化 MES：

- **主线（可不配 AI）**：订单 → 计划 → 排产 → 下发 → 派工 → 扫码报工 → 审核 → **自动计件工资**
- **辅线（可选）**：工厂助手、智能帮助、数据预警、APS 策略分析、每日简报

### 1.2 与全功能 MOM（如了云 MES）的差异

| 能力 | LightMes | 全功能 MOM |
|------|----------|------------|
| 计件工资自动算 | 核心 | 非重点 |
| 逐件报工 + 溯源 | 核心 | 部分支持 |
| 部署 | Python 轻量、无 Docker | 常 Java + 多模块 |
| MRP / 完整 WMS | 齐套检查为主 | 完整 MRP/FIFO |
| AI | 可选增值 | 视厂商而定 |

### 1.3 无 AI 网关也可用的能力

- 生产自动化流水线（OR-Tools 排期 + 自动下发/派工）
- 规则版每日简报
- 审核绿/黄/红规则预审
- 交期/缺料统计预测

---

## 二、上线与部署

详见 [宝塔部署.md](./宝塔部署.md)。本次自动化迭代要点：

1. **数据库**：`cd backend && alembic upgrade head`（含 `0041_automation_logs`、`0042_report_unit_prescreen`）
2. **后端**：重启 Uvicorn/Gunicorn
3. **Celery**：重启 worker + beat（新增任务见下表）
4. **前端**：`npm run build` 覆盖 admin-pro、frontend-h5、lightmes-miniapp
5. **健康检查**：`GET /api/health` → `build: 20260525-automation`

### Celery 任务

| 任务名 | 说明 | Beat |
|--------|------|------|
| `production.automation.pipeline` | 计划保存后自动排产/下发/派工 | 按需触发 |
| `ai.daily_brief.send` | 每日厂长简报 | 每天 **20:00**（见 [工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md)，含钉钉） |
| `audit.prescreen` | 报工提交后预审 | 按需触发 |
| `ai.alerts.scan` | 数据预警 | 8/12/16/20 点（原有） |

---

## 三、上线前基础数据检查

| 检查项 | 路径 | 未配置时自动化表现 |
|--------|------|------------------|
| 工序 + 工艺路线 | 主数据 → 工序/工艺路线 | 预检失败，无法自动建计划 |
| 型号×工序工价 | 主数据 → 工价 | 预检失败 |
| BOM | BOM 管理 | 缺料拦截（除非允许缺料） |
| 技能标签 | 系统 → 技能；工序绑技能 | 自动派工无人 |
| 人员产能 | 生产计划 → 产能配置 | 派工均衡偏差 |
| 报工形态 | 系统设置 → 报工形态 | **须为逐件**，预审/自动化仅支持件次模式 |
| Redis + Celery | 服务器 | 异步流水线/简报/预审不执行 |

---

## 四、生产自动化配置

**入口**：PC **智能中心 → 生产自动化**（`/system/automation-settings`）  
**权限**：`setting.manage`

### 4.1 开关说明

| 开关 | 默认 | 开启后行为 |
|------|------|------------|
| **总开关 enabled** | 关 | 关闭时所有自动动作不执行 |
| **订单确认后建计划** | 关 | 审核订单后自动创建 `planned` 计划 |
| **建计划后继续流水线** | 关 | 建计划后立即 OR-Tools 排期→可选下发→派工 |
| **计划保存后自动排产** | 关 | 创建/更新计划后 Celery 跑 pipeline |
| **自动确认下发** | 关 | 齐套通过后生成工单/任务 |
| **自动派工** | 关 | 按技能/车间/熟练度派工 |
| **允许缺料下发** | 关 | 缺料仍下发（风险自负） |
| **报工提交后预审** | 开 | 计算绿/黄/红标签 |
| **自动过班长审** | 关 | 仅 green 自动 leader_approved |
| **自动 QC 终审** | 关 | 强烈建议保持关闭 |
| **每日简报** | 关 | 定时推送规则/LLM 简报 |
| **简报模式** | rule | `rule` 规则模板 / `llm` 大模型 |

### 4.2 推荐套餐（附录 A 有 JSON）

| 套餐 | 适用 | 建议 |
|------|------|------|
| **保守** | 新上线/多品种 | 全关，仅用手动 + 智能排产按钮 |
| **标准** | 计件厂 | 开：预审 + 规则简报；半自动：计划保存后排产 |
| **激进** | 急单多、数据齐 | 订单确认→建计划→流水线全开 |

---

## 五、标准业务流程

### 5.1 手动模式（默认）

```
订单审核 → 手工建计划 → 齐套检查 → 确认下发 → 自动/手工派工
→ 员工扫码报工 → 班长/质检审核 → 工资自动出
```

### 5.2 半自动模式

```
订单审核 → 手工建计划 → [保存后 Celery 自动 OR-Tools 排期]
→ 人工确认下发 → 自动派工 → …
```

### 5.3 全自动模式（激进套餐）

```
订单审核 → [自动建计划] → [OR-Tools 排期] → [自动下发] → [自动派工]
→ 报工 → [预审/可选自动班长] → 质检 → 工资
```

**失败时**：查看 **自动化日志** + 消息通知；可改用手动「智能排产 → 采纳 OR-Tools」。

---

## 六、智能中心（AI 可选）

### 6.1 PC 入口（菜单「智能中心」）

| 功能 | 路径 |
|------|------|
| 工厂助手 | 首页按钮 / `?ai=1` |
| 智能帮助 | `/system/help` |
| AI 深度分析 | `/system/ai-deep` |
| AI 调用统计 | `/system/ai-stats` |
| 生产自动化 | `/system/automation-settings` |

### 6.2 H5 / 小程序

- H5 首页：**智能中心**宫格 + **今日简报**
- 小程序：**工作台**简报 + **功能 → 智能中心**

### 6.3 平台 AI 配置

平台运营 → **AI 模型** → 总开关 + 网关 + 默认模型 + Vision 模型。  
未配置时：助手/LLM 简报/APS LLM 解读不可用，**自动化与规则简报仍可用**。

---

## 七、审核预审与减负

- **绿**：附件齐全、无历史驳回 → 可开「自动过班长」
- **黄**：缺图或 Vision 偏低 → 人工优先看
- **红**：曾驳回或异常 → 必须人工

PC **件次报工审核**：支持按预审等级筛选；进入页面自动加载 **AI 批量摘要**（需 `ai.use`）。

---

## 八、每日简报与预警

- **规则简报**：不依赖 AI，聚合产量/待审/逾期
- **LLM 简报**：需 AI 网关；在自动化设置选 `mode: llm`
- **定时推送**：Celery 任务 `ai.daily_brief.send`，Beat **每天 20:00** 触发（`briefing.daily_enabled` 须开启）
- **推送通道**：站内（`ai.use`）+ 飞书/企微/钉钉 **管理群、全厂群**（详见 **[工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md)**）
- **首页卡片**：`GET /admin/ai/brief`（预览，不触发推送）

> 说明：设置页「推送小时 `daily_hour`」界面可填，**当前后端固定 20:00 发送**，该字段暂未生效。

预警：首页 **AI 数据预警**；阈值在 AI 预警配置中调整。

---

## 九、交期预测与 APS 策略分析

**入口**：生产计划编辑 → **APS 策略** Tab

- **交期风险条**：绿/黄/红（统计预测，非 ML）
- **策略卡片**：优先交期 / 均衡负荷 / 允许缺料下发
- **采纳**：链到现有「采纳 OR-Tools 并执行」

与了云「AI 智能体 APS」差异：LightMes 为 **规则评分 + OR-Tools + 可选 LLM 解读**，强调 **计件派工一键执行**。

---

## 十、自动化日志与故障排查

**入口**：生产自动化设置页 → **查看执行日志**  
**API**：`GET /admin/automation/logs`

| 现象 | 原因 | 处理 |
|------|------|------|
| 订单确认后无计划 | 预检失败（工价/BOM/工艺） | 补主数据；看日志 message |
| 计划保存后无反应 | Celery 未跑 / 总开关关 | 启 worker+beat；开 enabled |
| 自动下发失败 | 缺料且未允许缺料 | 补货或开 allow_shortage |
| 派工无人 | 无员工角色/技能不匹配 | 系统→用户/技能；工序绑技能 |
| 预审全黄 | 未上传报工附件 | 员工端补拍 |
| 简报未收到 | daily_enabled 关 / Celery 未跑 | 见 [工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md) 第七节 |

**预检演练**：`POST /admin/automation/dry-run`（传 `order_id` 或 `plan_id`）

---

## 十一、权限速查

| 权限 | 功能 |
|------|------|
| `setting.manage` | 自动化设置、日志 |
| `plan.manage` | 预检演练、计划 APS、流水线相关 |
| `report.audit` | 件次审核、预审查看 |
| `ai.use` | 工厂助手、LLM 简报、APS LLM 解读 |
| `ai.alert.view` | 预警卡片、H5 简报（部分） |

---

## 十二、三端操作速查

| 功能 | PC | H5 | 小程序管理 |
|------|-----|-----|------------|
| 生产自动化设置 | 智能中心→生产自动化 | — | 智能中心→生产自动化 |
| 今日简报 | 首页卡片 | 首页 | 工作台 |
| 智能中心 | 侧栏菜单 | 首页宫格 | 功能 Tab |
| APS 策略 | 计划编辑 Tab | — | 计划编辑 Tab |
| 预审筛选 | 件次报工审核 | — | 审核 Tab |
| 自动化日志 | 设置页 | — | 设置页 |

---

## 附录 A：推荐配置 JSON

### 保守

```json
{"enabled": false}
```

### 标准

```json
{
  "enabled": true,
  "on_plan_saved": {"run_schedule": true, "engine": "ortools", "auto_release": false, "auto_dispatch": false},
  "audit": {"prescreen_on_submit": true, "auto_leader_approve": false},
  "briefing": {"daily_enabled": true, "daily_hour": 8, "mode": "rule"}
}
```

### 激进

```json
{
  "enabled": true,
  "on_order_confirm": {"create_plan": true, "run_pipeline_after_create": true},
  "on_plan_saved": {"run_schedule": true, "engine": "ortools", "auto_release": true, "auto_dispatch": true, "allow_shortage": false},
  "audit": {"prescreen_on_submit": true, "auto_leader_approve": true},
  "briefing": {"daily_enabled": true, "daily_hour": 8, "mode": "llm"}
}
```

---

## 附录 B：API 速查

| 方法 | 路径 |
|------|------|
| GET/PUT | `/admin/automation/settings` |
| GET | `/admin/automation/logs` |
| POST | `/admin/automation/dry-run` |
| GET | `/admin/ai/brief` |
| GET | `/admin/ai/brief/latest` |
| GET | `/admin/plans/{id}/forecast` |
| GET | `/admin/plans/{id}/aps-strategy` |
| GET | `/h5/ai/brief` |

---

## 附录 C：文档索引

- [设备管理操作指南.md](./设备管理操作指南.md) — 设备档案、点检、保养计划
- [宝塔部署常见错误排查.md](./宝塔部署常见错误排查.md) — **503、缺 Pillow、Redis/Celery、端口占用、dist 404**
- [AI智能工厂操作SOP.md](./AI智能工厂操作SOP.md) — AI 专项短 SOP
- [AI集成说明.md](./AI集成说明.md) — API 与 Celery 明细
- [宝塔部署.md](./宝塔部署.md) — 部署步骤
- [小程序使用指南.md](./小程序使用指南.md) — 小程序配置
- [工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md) — **每日简报推飞书/企微/钉钉群、相关人员**
- [飞书消息推送部署指南.md](./飞书消息推送部署指南.md) — 飞书应用与 OAuth
- [钉钉消息推送部署指南.md](./钉钉消息推送部署指南.md) — 钉钉应用、Webhook 与 ActionCard 审核
- [报工与溯源形态.md](./报工与溯源形态.md) — 逐件报工说明

---

## 附录 D：竞品对照（了云 MES / LightMes）

| 维度 | 了云 MES | LightMes |
|------|----------|----------|
| 定位 | 全功能 MOM | 计件轻量 MES |
| 排产 | 原生 APS 模块 | OR-Tools + 自动化 pipeline |
| AI | APS 智能体宣传 | 规则 + 可选 LLM |
| 演示 | mes.llcoms.com | 自建租户 |
| 选型建议 | 要 MRP/WMS/委外全模块 | 要快速计件闭环 + 低部署成本 |

---

*文档随 `20260525-automation` 构建发布；界面以实际菜单为准。*
