# LightMes AI 集成 M2 规划（后续）

M1 已交付：平台多模型、老板问答、智能排产建议、交期分析、报工文字辅助、规则预警。

## 已完成（M2 完整）

1. **OR-Tools 约束排产**：`app/services/planning_optimizer.py`
2. **报工 Vision**：多模态模型 + 报工附件 URL
3. **审核批量 AI 摘要**
4. **RAG 帮助**：`docs/` 关键词检索 + LLM，`/admin/ai/help`、`/h5/ai/help`
5. **SSE 流式对话**：`POST /admin/ai/chat/stream`
6. **租户可选 Key**：`ai.gateway_override` → 系统设置 AI 网关
7. **小程序**：工厂助手 + 帮助页 + Phase E AI UI

## 仍可选

- 向量 embedding 升级 RAG（当前为关键词检索）
- 强化学习排产、Prophet/YOLO 等深度模型工程化

## 技术备注

- 保持「AI 只建议、人工确认写库」原则
- 预警规则阈值改为租户可配置（`tenant_setting`）
