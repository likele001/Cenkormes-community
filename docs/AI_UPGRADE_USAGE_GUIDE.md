# LightMes AI 能力升级 — 使用指南 (v2026.06)

> 适用版本: bgserver (104.152.50.138:8000) / 宝塔 Python 3.14 环境 / MySQL lightmes 库

---

## 一、要不要编译？

**不需要手动编译任何东西**。原因：

| 依赖 | 状态 | 说明 |
|------|------|------|
| **Prophet 1.3.0** | ✅ 已安装 | 使用自带 `cmdstanpy` 在首次 fit 时自动编译/缓存 Stan 模型（服务器上实测 8 行数据训练+预测正常） |
| **chromadb 0.6.3** | ✅ 已安装 | 纯 Python + SQLite 持久化，无需编译 |
| **scikit-learn 1.9.0** | ✅ 已安装 | 使用预编译 wheel，IsolationForest 推理 < 100 ms |
| **pandas 2.3.3 / numpy 1.26.4** | ✅ 已安装 | 已有 |
| **joblib 1.5.3** | ✅ 已安装 | 用于 ML 模型序列化到磁盘 |

验证命令 (已在 2026-06-20 执行通过):
```
python -c "import prophet; print(prophet.__version__)"
python -c "import chromadb; print(chromadb.__version__)"
python -c "from sklearn.ensemble import IsolationForest; print('ok')"
```

首次调用设备/良率预测时 Prophet 会编译 1 次 Stan 模型（约 10-30 秒），后续为 cached，推理很快。

---

## 二、本次新增一览

### 2.1 新增文件（共约 19 个）

**RAG 向量检索模块**
- `backend/app/services/ai/rag_vector.py` — 核心: ChromaDB 初始化、embedding 调用、语义搜索、混合检索
- `backend/app/services/ai/rag_indexer.py` — 文档变更检测 + Celery 定时索引

**预测模型模块**
- `backend/app/services/ai/predict/__init__.py` — 包入口
- `backend/app/services/ai/predict/equipment_predictor.py` — 设备点检时序预测 (Prophet) + 异常检测 (IsolationForest)
- `backend/app/services/ai/predict/yield_predictor.py` — 良率预测 + 全厂异常检测
- `backend/app/services/ai/predict/model_manager.py` — 模型生命周期管理（LRU 缓存 + joblib 磁盘持久化）

**AI Agent 工具模块**
- `backend/app/services/ai/agent/__init__.py`
- `backend/app/services/ai/agent/tools_registry.py` — 工具注册表（自动注册，OpenAI function calling 格式）
- `backend/app/services/ai/agent/builtin_tools.py` — 8 个内置工具（见§4）

**L3+ 分析模块（深度智能增强）**
- `backend/app/services/ai/twin/enhanced_twin.py` — 车间孪生增强（负荷 + 瓶颈识别 + 历史趋势 + 未来负载预测）
- `backend/app/services/ai/causal/enhanced_causal.py` — 因果推理增强（工序良率分解 + 前后期对比 + 相关性矩阵）
- `backend/app/services/ai/quality/enhanced_quality.py` — 质量基因增强（关键词 + LLM 语义提取 + 趋势）
- `backend/app/services/ai/pricing/enhanced_pricing.py` — 计价建议增强（多因子效率/需求量）

**反馈模块**
- `backend/app/services/ai/feedback.py` — 用户纠正 AI 回答自动入库 + 写入 ChromaDB 知识库

**主动推荐模块**
- `backend/app/services/ai/proactive.py` — 工单交期/良率下降/设备风险/待派工扫描

**数据库迁移**
- `backend/alembic/versions/0055_rag_feedback.py` — `ai_rag_feedbacks` 表
- `backend/alembic/versions/0056_predict_models.py` — `ai_predict_models` 表

### 2.2 修改文件（约 8 个）

| 文件 | 改动 |
|------|------|
| `app/core/config.py` | 新增 RAG 配置项（CHROMA_DIR / CHUNK_SIZE / OVERLAP / HYBRID_WEIGHT / EMBEDDING_MODEL） |
| `app/api/admin/ai/router.py` | 新增 11 个 API 端点（§5 详述） |
| `app/tasks/ai.py` | 新增 `ai.rag.reindex`、`ai.predict.train_all`、`ai.predict.train_equipment` Celery 任务 |
| `app/celery_app.py` | 新增定时任务：每日 3:30 RAG 重索引 + 每周日预测模型重训练 |
| `app/services/ai/digital_twin.py` | 原规则版保留 + `workshop_twin_enhanced()` 重定向 |
| `app/services/ai/causal_inference.py` | 同上，增强版 `analyze_yield_causes_enhanced()` |
| `app/services/ai/visual_quality.py` | 同上，增强版 `extract_quality_patterns()` / `auto_defect_dictionary()` |
| `app/services/ai/pricing_ai.py` | 同上，增强版 `suggest_prices_enhanced()` |

### 2.3 新增数据库表

**`ai_rag_feedbacks`（11 列）**

| 列 | 类型 | 用途 |
|----|------|------|
| id | int PK | 主键 |
| tenant_id | int | 租户隔离 |
| user_id | int | 提交用户 |
| conversation_id | int | （可选）对话 ID |
| message_id | int | （可选）消息 ID |
| query | text | 用户提问原文 |
| answer | text | AI 原回答 |
| feedback_type | varchar(20) | `thumb_up` / `thumb_down` / `corrected` |
| corrected_answer | text | 用户手动修改的正确答案 |
| processed | bool | 是否已加入知识库 |
| created_at | datetime | 提交时间 |

**`ai_predict_models`（9 列）**

| 列 | 类型 | 用途 |
|----|------|------|
| id | int PK | 主键 |
| tenant_id | int | 租户 |
| model_type | varchar(32) | `equipment_prophet` / `yield_prophet` / `equipment_if` / `yield_if` |
| model_key | varchar(128) | 如 equipment_id 或 'factory' |
| trained_at | datetime | 训练时间 |
| metrics_json | text | 训练指标 JSON（数据点数量/MAE 等） |
| status | varchar(16) | `active` / `stale` |
| data_points | int | 训练数据点数 |
| model_size_bytes | int | 磁盘模型大小 |

> 表已通过 alembic 自动迁移（2026-06-20 执行），无需手工建表。

---

## 三、RAG 向量检索 — 使用说明

### 3.1 前置条件
需要管理员先配置 AI 网关（Platform Settings > AI Gateway）:
- Base URL（如 `https://api.deepseek.com/v1` 或 `https://open.bigmodel.cn/api/paas/v4`）
- API Key
- 默认模型（如 `deepseek-chat`）

RAG 复用同一网关的 embedding 端点（`/embeddings`），无需额外配置。

### 3.2 首次使用 — 构建索引

**方式 1：通过管理后台 API**

```
POST /api/admin/ai/help/reindex  (Body: {})
```

**方式 2：Curl 示例（需替换 cookie/token）**
```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/ai/help/reindex' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{}'
```

返回：
```json
{"code":200,"msg":"","data":{"status":"force_reindexed","files":6,"total_chunks":30}}
```

**方式 3：Celery 每日自动索引** — 凌晨 3:30 自动检查 `docs/*.md` 变更并增量更新。

索引文件存储位置: `backend/data/chroma_db/` (SQLite 持久化)

### 3.3 文档源

系统从 `backend/docs/` 目录读取所有 `.md` 文件（通常含 `lightmes-guide.md`、`quickstart.md` 等）。
如需添加文档，直接把 `.md` 文件放入该目录，下次 reindex 即自动索引。

### 3.4 使用语义搜索

**前端调用 `help` 端点（建议）：**
```
GET /api/admin/ai/help?query=订单怎样创建&top_k=3
```
返回带语义匹配分数的回答（自动调用向量检索，原关键词搜索作为 fallback）。

**原始搜索结果调试接口：**
```
GET /api/admin/ai/help/search?q=生产流程&top_k=5
```

### 3.5 用户反馈闭环

```
POST /api/admin/ai/feedback/submit
{
  "query": "如何设置自动派工？",
  "answer": "AI的原始回答…",
  "feedback_type": "corrected",
  "corrected_answer": "正确答案：在 生产管理 > 工单 > 设置自动派工策略…"
}
```

`feedback_type: corrected` 时，系统会把 `corrected_answer` 作为一条新知识 chunk **自动写入 ChromaDB**，下次用户查询相关问题时，会首先匹配到这条人工纠正的答案。

### 3.6 反馈统计

```
GET /api/admin/ai/feedback/stats
→ {total: 15, by_type: {corrected: 5, thumb_up: 8, thumb_down: 2}, correction_rate: 0.33}
```

---

## 四、预测模型 (Prophet + IsolationForest) — 使用说明

### 4.1 模型种类

| 模型 | 文件 | 数据要求 | 输出 |
|------|------|----------|------|
| **设备点检趋势** (Prophet) | `predict/equipment_predictor.py` | ≥7 天数据点 | 未来 7 天点检频次预测 + 健康评分 |
| **设备点检异常检测** (IF) | `predict/equipment_predictor.py` | ≥7 天数据点 | 0/1 异常标记 + 异常分数 |
| **工序良率趋势** (Prophet) | `predict/yield_predictor.py` | ≥7 天数据点 | 各工序未来 7 天良率预测 |
| **全厂良率异常检测** (IF) | `predict/yield_predictor.py` | ≥7 天数据点 | 异常日期列表 + 分数 |

### 4.2 训练设备预测模型（手动触发）

```
POST /api/admin/ai/deep/equipment/1/train
（body 可为空 {}）
```
返回：
```json
{
  "ok": true,
  "data_points": 45,
  "prophet_saved": true,
  "isolation_forest_saved": true
}
```

> 首次训练需要 Prophet 编译 Stan 模型（~10-30 秒），之后都走缓存，非常快。

### 4.3 获取增强版设备健康

```
GET /api/admin/ai/deep/equipment-health-enhanced
```

返回每项设备：

| 字段 | 含义 |
|------|------|
| `equipment_id` / `code` / `name` | 设备基本信息 |
| `health_score` (0-100) | 规则分 + 预测分融合 |
| `base_score` (0-100) | 仅规则评分（点检频次） |
| `predicted_score_7d` (0-100) | Prophet 预测的未来 7 天健康分（有 ML 模型时才返回） |
| `trend` | `improving` / `stable` / `declining` |
| `anomaly_detected` | bool — 是否检测到异常点检模式 |
| `anomaly_score` | 0~1 float |
| `has_ml_model` | 是否已完成 ML 训练 |
| `level` | `good` / `watch` / `risk` |
| `suggestion` | 推荐操作文字 |

### 4.4 良率预测 & 异常检测

```
GET /api/admin/ai/deep/yield/predictions
→ {predictions: [{process_id:1, predicted_avg:0.92, historical_avg_30d:0.90, trend:"improving", prediction_series:[{date:"2026-06-21", yhat:0.925}, ...]}], total_processes: 5}
```

```
GET /api/admin/ai/deep/yield/anomalies
→ {total_days:90, anomaly_count:3, anomalies:[{date:"2026-05-15", yield_rate:0.76, anomaly_score:-0.123}, ...]}
```

### 4.5 定时自动训练

- **每周日 03:00** — 系统通过 Celery beat 自动调用 `ai.predict.train_all`，对所有租户所有设备/工序重新训练。
- 如果你有特别感兴趣的某台设备，也可以通过 `/deep/equipment/{id}/train` 单独触发。

预测模型存储在 `backend/data/predict_models/<tenant_id>_<key>.joblib`，每个模型约 50-200 KB。

---

## 五、L3+ 深度分析模块 — 使用说明

### 5.1 车间孪生增强版

```
GET /api/admin/ai/deep/twin-enhanced
```

返回：
- `workshops` — 各车间 pending/working 任务数
- `processes` — 工序级任务分布
- `bottleneck` — 自动识别的瓶颈工序（队列 > 阈值）
- `trend` — 近 7 天的历史任务量趋势

```
GET /api/admin/ai/deep/bottleneck
→ {bottlenecks: [{process_id:5, workshop:"装配", pending: 22}], threshold: 5}
```

### 5.2 因果推理增强版

```
GET /api/admin/ai/deep/causal-enhanced
```

返回：
- `total_good` / `total_bad` / `overall_yield_rate` — 全厂 30 天汇总
- `trend` — `improving` / `stable` / `declining`（前15天 vs 后15天对比）
- `process_breakdown` — 每工序良率明细（含 good/bad/rate）
- `low_yield_processes` — 低良率 Top N 工序
- `hypotheses` — 系统自动生成的因果假设（文字）

```
GET /api/admin/ai/deep/causal/correlation
→ {correlations: [{process_a:1, process_b:2, correlation:0.87}, ...]}
```
> 相关性 >0.6 的工序对会高亮，说明这两个工序的不良波动高度同步，可能存在共同根因（如来料问题、共享设备问题）。

### 5.3 质量基因库增强版

```
GET /api/admin/ai/deep/quality-patterns
```

综合 **关键词规则** + **LLM 语义提取**，从近 500 条 `ReportUnit` 不良备注中提取缺陷模式标签和频次。

返回：
```json
{
  "scanned_items": 352,
  "patterns_count": 12,
  "patterns": [
    {"tag": "划痕", "count": 48, "samples": ["A面划痕严重", "外壳划伤约3cm"]},
    {"tag": "色差", "count": 31, "samples": ["颜色偏黄", "与样板色不一致"]},
    ...
  ]
}
```

```
GET /api/admin/ai/deep/quality-dictionary
→ {dictionary: [{code:"DEF_XH", label:"铣削", sample_count:48}, ...]}
```

### 5.4 计价建议增强版

```
GET /api/admin/ai/deep/pricing-enhanced
```

返回每 SKU+工序的计价调整建议，考虑多个因子：

| 字段 | 说明 |
|------|------|
| `current_price` / `suggested_price` | 当前 / 建议单价 |
| `adjustment_pct` | 调整幅度（%），如 `+15.0` |
| `reasons` | 例如 `["效率偏高(1.3x)", "高需求(200次)"]` |
| `efficiency` / `volume_score` | 各因子详细得分 |

---

## 六、AI Agent 工具 (Function Calling)

`tools_registry.registry` 在首次调用时自动注册全部 8 个内置工具，无需手工初始化。

### 6.1 已注册的 8 个工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `query_orders` | 按状态查询工单 | `status` (pending/processing/completed), `code_contains`, `limit` |
| `query_tasks` | 按状态查询任务 | `status`, `limit` |
| `query_equipment_status` | 获取设备列表与状态 | 无参数 |
| `query_materials` | 物料查询 | 无参数 |
| `query_reports` | 近 N 天报工统计 + 良率 | `days`(默认 7) |
| `query_knowledge` | 知识库向量搜索 | `question` (必须) |
| `query_yield_prediction` | 良率预测结果 | 无参数 |
| `create_reminder` | 创建文字提醒 | `content` |

### 6.2 在 Python 中直接使用

```python
from app.services.ai.agent.tools_registry import registry

# 1) 获取 OpenAI function calling 格式工具列表
tools = registry.get_tools()  # 可直接传给 client.chat.completions.create(tools=tools)

# 2) 执行某个工具
result = registry.execute(
    "query_orders",
    {"status": "pending", "limit": 5},
    {"db": db_session, "tenant_id": user.tenant_id}
)
print(result)  # "- WO2026060001 (pending) due 2026-06-30 ...\n"
```

### 6.3 接入对话助手

在 `scenes.py` / `client.py` 中可以把 `registry.get_tools()` 作为 OpenAI `tools` 参数传入，并在 `tool_call` 响应中调用 `registry.execute(name, args, context)` 执行工具后再做二次总结回答，实现多轮 Agent 对话。目前版本提供的是**工具执行核心**，前端对接可按需调用。

---

## 七、主动推荐 (Proactive)

```
GET /api/admin/ai/recommendations
```

返回当前需要关注的事项（每类最多 3 条）:

| 规则 | 触发条件 | 示例 |
|------|----------|------|
| `order_due_soon` | 未来 7 天内到期且尚未完成的工单 | "工单 WO202606-0032 临近交期" |
| `yield_drop` | 近 7 天良率比前 23 天下降 > 5% | "良率从 95% 下降到 88%" |
| `equipment_risk` | 某设备 ML 预测健康分 < 50 或 trend=declining | "CNC-03 健康分下降至 42" |
| `pending_dispatch` | 当前 pending 任务 ≥ 10 个 | "当前待派工 38 个，建议及时分配" |

> AI 管理员可在管理界面看到这一卡片，或通过定时任务主动通知。

---

## 八、新增 API 端点总览

所有端点统一在 `/api/admin/ai/` 下，返回格式 `{code, msg, data}`，需要 `ai.use` 权限；涉及修改/管理操作需要 `setting.manage`。

### 8.1 RAG 相关

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| POST | `/help/reindex` | 强制重建文档向量索引 | `ai.use` + `setting.manage` |
| POST | `/feedback/submit` | 提交用户反馈（纠正 AI 回答） | `ai.use` |
| GET | `/feedback/stats` | 获取反馈统计 | `ai.use` |
| GET | `/feedback/recent` | 最近 N 条反馈记录 | `ai.use` |

### 8.2 预测模型相关

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| POST | `/deep/equipment/{equipment_id}/train` | 训练单台设备预测模型 | `ai.use` |
| GET | `/deep/equipment-health-enhanced` | 获取融合 ML 预测的设备健康分 | `ai.use` |
| GET | `/deep/yield/predictions` | 获取各工序的良率预测 | `ai.use` |
| GET | `/deep/yield/anomalies` | 获取全厂良率异常检测结果 | `ai.use` |

### 8.3 L3+ 深度分析相关

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/deep/twin-enhanced` | 车间孪生增强（负荷 + 瓶颈 + 趋势） | `ai.use` |
| GET | `/deep/bottleneck` | 工序瓶颈识别 Top-N | `ai.use` |
| GET | `/deep/causal-enhanced` | 因果推理增强版（趋势+低良率+LLM假设） | `ai.use` |
| GET | `/deep/causal/correlation` | 工序间不良率相关性矩阵 | `ai.use` |
| GET | `/deep/quality-patterns` | 缺陷模式自动提取（关键词+LLM） | `ai.use` |
| GET | `/deep/quality-dictionary` | 自动缺陷代码词典 | `ai.use` |
| GET | `/deep/pricing-enhanced` | 多因子动态计价建议 | `ai.use` |
| GET | `/recommendations` | 主动推荐（交期/良率/设备/派工） | `ai.use` |

### 8.4 已有端点（保持不变）

`/chat`, `/chat/stream`, `/deep/overview`, `/deep/equipment-health`, `/deep/report-risk`, `/deep/quality-genes`, `/deep/pricing`, `/stats`, `/alerts/*`, `/alert-settings/*`, `/prompt-settings/*`, `/gateway-settings/*`, `/brief`, `/brief/latest` 等接口完全兼容，**调用方式不变**；其中 `equipment-health` / `quality-genes` / `pricing` 等内部实现走了规则+增强版双通道。

---

## 九、定时任务 (Celery Beat)

| 任务名 | 触发时间 | 功能 |
|--------|----------|------|
| `ai.rag.reindex` | 每日 03:30 | 检查 `docs/*.md` 文件变更 → 增量向量化 → 写入 ChromaDB |
| `ai.predict.train_all` | 每周日 03:00 | 遍历所有租户 → 训练所有设备的 Prophet 预测模型 |

> 这些任务如果在宝塔面板使用 `celery beat` 启动需要确认 `app/celery_app.py` 中 `schedule` 字典已被加载。当前生产部署 beat 正确运行（通过 `ps aux | grep celery` 验证有 beat 进程）。

---

## 十、故障排查

### 10.1 调用任何 AI 接口返回 401

- **原因**: 未登录 / Token 过期
- **解决**: 重新登录管理后台后调用

### 10.2 RAG 回答与原关键词版一致，没看到语义搜索效果

- **原因 1**: 尚未执行 `reindex`，ChromaDB 为空
  - `curl -X POST /help/reindex` 触发首次索引
- **原因 2**: Embedding API 不可用（网关未配置或网络不通）
  - 检查 `Platform Settings > AI Gateway` 是否配置
  - 检查 `/api/admin/ai/stats` 确认 embedding 是否有调用记录
- **原因 3**: 文档量太少（< 3 个）
  - 在 `backend/docs/` 中增加 `.md` 文档

验证 ChromaDB 目录状态：
```
ls -la /www/wwwroot/lightmes/backend/data/chroma_db/
```

### 10.3 设备健康分数没有 predicted_score_7d

- **原因**: 未训练模型（某设备数据不足 7 天）
- **解决**:
  - 先有真实的 `EquipmentCheck` 点检数据（≥7 天）
  - 调用 `/deep/equipment/{id}/train` 触发训练
  - 或等待周日凌晨的自动训练任务
- **验证** (服务器侧):
  ```
  ls -la /www/wwwroot/lightmes/backend/data/predict_models/
  ```
  如果目录下有 `equipment_prophet/<tenant_id>_<equipment_id>.joblib`，说明模型已生成。

### 10.4 Prophet 首次训练卡住 10+ 秒

这是 Stan 编译器在首次运行时**自动编译 C++ 模型源码**，属于正常行为（此后走编译缓存，毫秒级启动）。
- 如想加速：`pip install cmdstanpy` 后 `python -m cmdstanpy.install_cmdstan` 预先构建（其实 Prophet 已经自带此步骤）
- Stan 编译目录：`/root/.cmdstan/`

### 10.5 测试 Prophet 能否工作

```bash
cd /www/wwwroot/lightmes/backend
source /www/server/pyporject_evn/lightmes/bin/activate
python -c "
import pandas as pd
from prophet import Prophet
df = pd.DataFrame([
    {'ds': '2026-06-10', 'y': 10},
    {'ds': '2026-06-11', 'y': 12},
    {'ds': '2026-06-12', 'y': 15},
    {'ds': '2026-06-13', 'y': 11},
    {'ds': '2026-06-14', 'y': 13},
    {'ds': '2026-06-15', 'y': 14},
    {'ds': '2026-06-16', 'y': 16},
    {'ds': '2026-06-17', 'y': 12},
])
m = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
m.fit(df)
future = m.make_future_dataframe(periods=3)
forecast = m.predict(future)
print('Prophet works. Last predicted yhat:', round(float(forecast['yhat'].iloc[-1]), 2))
"
```

预期输出: `Prophet works. Last predicted yhat: 13.xx`

### 10.6 调试某具体模块导入

```bash
python -c "from app.services.ai.predict.equipment_predictor import equipment_health_scores_enhanced; print('OK')"
python -c "from app.services.ai.rag_vector import semantic_search; print('OK')"
python -c "from app.services.ai.agent.tools_registry import registry; print(len(registry.get_tools()), 'tools')"
```

### 10.7 uvicorn 日志

后端 uvicorn 的 stdout/stderr 重定向在 `/tmp/uvicorn.log`：
```
tail -100 /tmp/uvicorn.log
```

如果发现 `SyntaxError` 或 `ImportError`，说明某文件修改错误；定位后通知我处理。

### 10.8 新增的文件清单

快速确认部署完整度：
```
ls /www/wwwroot/lightmes/backend/app/services/ai/predict/*.py
ls /www/wwwroot/lightmes/backend/app/services/ai/agent/*.py
ls /www/wwwroot/lightmes/backend/app/services/ai/twin/enhanced_twin.py
ls /www/wwwroot/lightmes/backend/app/services/ai/causal/enhanced_causal.py
ls /www/wwwroot/lightmes/backend/app/services/ai/quality/enhanced_quality.py
ls /www/wwwroot/lightmes/backend/app/services/ai/pricing/enhanced_pricing.py
ls /www/wwwroot/lightmes/backend/app/services/ai/rag_vector.py
ls /www/wwwroot/lightmes/backend/app/services/ai/rag_indexer.py
ls /www/wwwroot/lightmes/backend/app/services/ai/feedback.py
ls /www/wwwroot/lightmes/backend/app/services/ai/proactive.py
ls /www/wwwroot/lightmes/backend/alembic/versions/0055_rag_feedback.py
ls /www/wwwroot/lightmes/backend/alembic/versions/0056_predict_models.py
```

### 10.9 数据库状态查询

```sql
-- 已建表
DESCRIBE ai_rag_feedbacks;
DESCRIBE ai_predict_models;

-- 反馈统计
SELECT feedback_type, COUNT(*) FROM ai_rag_feedbacks GROUP BY feedback_type;

-- 模型元数据
SELECT model_type, status, COUNT(*) FROM ai_predict_models GROUP BY model_type, status;
```

---

## 十一、快速上手测试流程（建议首次使用按此走一遍）

1. **配置 AI 网关**：登录管理后台 → Platform Settings → AI Gateway，填入 Base URL 和 API Key，保存
2. **构建文档索引**:
   ```
   POST /api/admin/ai/help/reindex  Body: {}
   ```
3. **测试语义搜索**：
   ```
   GET /api/admin/ai/help?query=如何设置自动派工
   ```
4. **测试用户反馈闭环**：
   ```
   POST /api/admin/ai/feedback/submit
   {"query":"如何设置自动派工",
    "answer":"系统原有回答…",
    "feedback_type":"corrected",
    "corrected_answer":"正确答案: 生产管理 > 工单 > 自动派工策略"}
   ```
5. **再次查询同一问题验证改进**：
   ```
   GET /api/admin/ai/help?query=如何设置自动派工   ← 应优先返回用户纠正的答案
   ```
6. **触发设备预测训练**（任选一台设备 ID）:
   ```
   POST /api/admin/ai/deep/equipment/1/train
   ```
7. **查看增强版健康分**:
   ```
   GET /api/admin/ai/deep/equipment-health-enhanced
   ```
8. **查看 L3+ 分析**（挑几个）：
   ```
   GET /api/admin/ai/deep/twin-enhanced
   GET /api/admin/ai/deep/bottleneck
   GET /api/admin/ai/deep/causal-enhanced
   GET /api/admin/ai/deep/quality-patterns
   GET /api/admin/ai/deep/pricing-enhanced
   GET /api/admin/ai/recommendations
   ```

---

## 十二、性能 / 资源占用参考

| 功能 | 内存/进程 | 时间 | 备注 |
|------|----------|------|------|
| ChromaDB (空) | ≈30 MB | - | 按需加载 |
| ChromaDB (1000 chunks) | ≈80 MB | search: 50ms | 与向量维度相关 |
| Prophet 训练 (90 天数据) | ≈300 MB peak | 10-30 s (首测) | 后续走缓存 |
| Prophet 推理 (7 天) | <50 MB | <1 s | 从 joblib 加载 |
| IsolationForest 推理 | <20 MB | <200 ms | 极轻量 |
| Embedding API 调用 | 常驻进程内存不增 | ≈1-2 s/批 | 通过网关走外网 API |

服务器可用内存: **约 11 GB 共，目前已用 8.8 GB**，建议保持可用 ≥1.5 GB（Prophet 首次训练峰值 ~300 MB），整体是安全的。

---

## 十三、文件清单汇总

### 新建文件（按模块分组）

```
backend/app/services/ai/
├── rag_vector.py                   ← 向量检索核心
├── rag_indexer.py                  ← 索引管理（含定时）
├── feedback.py                     ← 用户反馈闭环
├── proactive.py                    ← 主动推荐引擎
│
├── predict/
│   ├── __init__.py
│   ├── equipment_predictor.py      ← 设备 Prophet + IF
│   ├── yield_predictor.py          ← 良率 Prophet + IF
│   └── model_manager.py            ← LRU 缓存 + 磁盘持久化
│
├── agent/
│   ├── __init__.py
│   ├── tools_registry.py           ← 工具注册表（auto-init）
│   └── builtin_tools.py            ← 8 个内置工具实现
│
├── twin/
│   ├── __init__.py
│   └── enhanced_twin.py            ← 车间孪生增强
│
├── causal/
│   ├── __init__.py
│   └── enhanced_causal.py          ← 因果推理增强
│
├── quality/
│   ├── __init__.py
│   └── enhanced_quality.py         ← 缺陷模式提取
│
└── pricing/
    ├── __init__.py
    └── enhanced_pricing.py         ← 多因子动态计价

backend/alembic/versions/
├── 0055_rag_feedback.py           ← ai_rag_feedbacks 表
└── 0056_predict_models.py         ← ai_predict_models 表
```

### 修改文件

```
backend/app/core/config.py            ← 新增 RAG 配置项
backend/app/api/admin/ai/router.py    ← 新增 11 个 API 端点
backend/app/tasks/ai.py               ← 新增 3 个 Celery 任务
backend/app/celery_app.py             ← 新增 2 个定时任务
backend/app/services/ai/digital_twin.py    ← 保留原接口 + 增强重定向
backend/app/services/ai/causal_inference.py ← 保留原接口 + 增强重定向
backend/app/services/ai/visual_quality.py   ← 保留原接口 + 增强重定向
backend/app/services/ai/pricing_ai.py       ← 保留原接口 + 增强重定向
backend/requirements.txt              ← 新增 5 个依赖声明
```

---

**文档结束。** 如发现任何端点 / 模块 / 数据表缺失或异常，请告知具体错误信息，我会修复。
