# 报工 · report(report_units)

> 实现：`api/admin/production/report_units.py`；schema：`schemas/report.py`；表 `reports`、`report_units`。
> 报工是生产数据采集核心，支持逐条上报、逐件核算、质检、审核与工资联动。

## 上报（POST）
`ReportSubmitIn`：
| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | int ≥1 | 关联任务 |
| good_qty | int ≥0 | 合格数 |
| bad_qty | int ≥0 | 不良数（默认0） |
| remark | string ≤500 | 备注 |
| attachment_ids | string ≤512 | 附件ID(逗号分隔) |

`ReportOut`：id/tenant_id/task_id/report_user_id/good_qty/bad_qty/remark/attachment_ids/status/created_at/updated_at

## 列表查询
| 参数 | 说明 |
|------|------|
| task_id / user_id | 按任务/用户过滤 |
| status | 状态 |
| prescreen_level | 预筛层级 |
| pending_audit | true=仅待审(submitted/leader_approved) |
| risk_first | true=高风险优先 |
| offset / limit | 分页（limit≤200，默认50） |

## 质检（InspectionResultIn）
`template_item_id`(必)、`result`(pass/fail/na)、`measured_value`(≤64)、`defect_code_id`、`remark`(≤500)。

## 审核（AuditActionIn / QcApproveIn）
- 审核动作传 `reason`(≤500)；QC 放行传 `qc_attachment_ids` + `remark`
- **审核钩子**：提交后、审批通过/驳回后触发报告 work hook（用独立 DB session，避免阻塞/回滚薪酬看板流程）

## 联动
- 报工合格→计件工资（salary）
- 前端入口：H5 报工页、小程序批量报工（php 端上报 / report/unit）
