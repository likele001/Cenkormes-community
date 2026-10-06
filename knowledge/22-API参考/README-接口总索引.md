# API 接口总索引（自动生成基线 + 模块文档）

> 本目录含两类内容：
> - **模块文档**（人工维护，字段来自真实 schema）：各核心业务模块的接口/字段/二次开发注意
> - **接口总索引**（自动扫描生成）：全部 250+ 端点的路径清单

## 模块文档导航
| 模块 | 文档 |
|------|------|
| 报工 | [模块-报工report.md](模块-报工report.md) |
| 订单 | [模块-订单order.md](模块-订单order.md) |
| 工资条 | [模块-工资条salary.md](模块-工资条salary.md) |
| 采购 | [模块-采购purchase.md](模块-采购purchase.md) |
| 财务 | [模块-财务finance.md](模块-财务finance.md) |
| 库存 | [模块-库存warehouse.md](模块-库存warehouse.md) |
| 设备（示例） | [功能示例-设备管理.md](功能示例-设备管理.md) |

## 接口索引说明

> 由后端路由扫描生成。前缀：后台 /admin/*、员工H5 /h5/*、平台 /platform/*、小程序 /miniapp/*、开放回调 /feishu|/wecom|/dingtalk、认证 /auth|/v1、实时 /ws。
> 自动生成日期：2026-09-13。逐接口详细参数见各模块文档。

## admin/ai/router.py  （47 端点）

- `- `post"`/chat",`
- `- `post"`/chat/stream",`
- `- `post"`/help",`
- `- `get"`/help/search",`
- `- `post"`/help/reindex",`
- `- `get"`/gateway-settings",`
- `- `put"`/gateway-settings",`
- `- `post"`/plan/{plan_id}/analyze",`
- `- `post"`/plan/{plan_id}/schedule-suggest",`
- `- `post"`/plan/{plan_id}/schedule-optimize",`
- `- `post"`/plan/{plan_id}/schedule-apply",`
- `- `get"`/alerts",`
- `- `post"`/alerts/run",`
- `- `get"`/alert-settings",`
- `- `put"`/alert-settings",`
- `- `post"`/audit/summary",`
- `- `post"`/report-units/{unit_id}/vision",`
- `- `get"`/deep/overview",`
- `- `get"`/deep/causal",`
- `- `get"`/deep/quality-genes",`
- `- `get"`/deep/pricing",`
- `- `get"`/deep/digital-twin",`
- `- `get"`/deep/equipment-health",`
- `- `get"`/stats",`
- `- `get"`/models",`
- `- `get"`/prompt-settings",`
- `- `put"`/prompt-settings",`
- `- `get"`/conversations",`
- `- `delete"`/conversations/{conversation_id}",`
- `- `get"`/brief",`
- `- `get"`/brief/latest",`
- `- `post"`/deep/equipment/{equipment_id}/train",`
- `- `get"`/deep/yield/anomalies",`
- `- `get"`/deep/yield/predictions",`
- `- `get"`/deep/equipment-health-enhanced",`
- `- `post"`/feedback/submit",`
- `- `get"`/feedback/stats",`
- `- `get"`/feedback/recent",`
- `- `get"`/recommendations",`
- `- `get"`/deep/twin-enhanced",`
- `- `get"`/deep/bottleneck",`
- `- `get"`/deep/causal-enhanced",`
- `- `get"`/deep/causal/correlation",`
- `- `get"`/deep/quality-patterns",`
- `- `get"`/deep/quality-dictionary",`
- `- `get"`/deep/pricing-enhanced",`
- `- `post"`/voice-order/parse",`
- `post` `/chat", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/chat/stream", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/help", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/help/search", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/help/reindex", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `get` `/gateway-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `put` `/gateway-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `post` `/plan/{plan_id}/analyze", dependencies=[Dependsrequire_permissions["ai.use", "plan.manage"]`
- `post` `/plan/{plan_id}/schedule-suggest", dependencies=[Dependsrequire_permissions["ai.use", "plan.manage"]`
- `post` `/plan/{plan_id}/schedule-optimize", dependencies=[Dependsrequire_permissions["ai.use", "plan.manage"]`
- `post` `/plan/{plan_id}/schedule-apply", dependencies=[Dependsrequire_permissions["ai.use", "plan.manage"]`
- `get` `/alerts", dependencies=[Dependsrequire_permissions["ai.alert.view"]`
- `post` `/alerts/run", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/alert-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `put` `/alert-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `post` `/audit/summary", dependencies=[Dependsrequire_permissions["ai.use", "report.audit"]`
- `post` `/report-units/{unit_id}/vision", dependencies=[Dependsrequire_permissions["ai.use", "report.audit"]`
- `get` `/deep/overview", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/causal", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/quality-genes", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/pricing", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/digital-twin", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/equipment-health", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/stats", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/models", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/prompt-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `put` `/prompt-settings", dependencies=[Dependsrequire_permissions["ai.use", "setting.manage"]`
- `get` `/conversations", dependencies=[Dependsrequire_permissions["ai.use"]`
- `delete` `/conversations/{conversation_id}", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/brief", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/brief/latest", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/deep/equipment/{equipment_id}/train", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/yield/anomalies", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/yield/predictions", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/equipment-health-enhanced", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/feedback/submit", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/feedback/stats", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/feedback/recent", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/recommendations", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/twin-enhanced", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/bottleneck", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/causal-enhanced", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/causal/correlation", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/quality-patterns", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/quality-dictionary", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/deep/pricing-enhanced", dependencies=[Dependsrequire_permissions["ai.use"]`

## admin/ai_employee/router.py  （11 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/tools"`
- `- `get"`/{employee_id}"`
- `- `put"`/{employee_id}"`
- `- `delete"`/{employee_id}"`
- `- `post"`/{employee_id}/toggle"`
- `- `get"`/{employee_id}/conversations"`
- `- `get"`/{employee_id}/conversations/{conversation_id}/messages"`
- `- `get"`/{employee_id}/logs"`
- `- `get"`/{employee_id}/stats"`
- `get` `"`
- `post` `"`
- `get` `/tools"`
- `get` `/{employee_id}"`
- `put` `/{employee_id}"`
- `delete` `/{employee_id}"`
- `post` `/{employee_id}/toggle"`
- `get` `/{employee_id}/conversations"`
- `get` `/{employee_id}/conversations/{conversation_id}/messages"`
- `get` `/{employee_id}/logs"`

## admin/approval/router.py  （6 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/{flow_id}"`
- `- `put"`/{flow_id}"`
- `- `delete"`/{flow_id}"`
- `- `put"`/{flow_id}/steps"`
- `get` `"`
- `post` `"`
- `get` `/{flow_id}"`
- `put` `/{flow_id}"`
- `delete` `/{flow_id}"`

## admin/assistant/router.py  （5 端点）

- `- `get"`/tools",`
- `- `post"`/chat",`
- `- `post"`/act",`
- `- `get"`/history",`
- `- `get"`/history/{conversation_id}/messages",`
- `get` `/tools", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/chat", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/act", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/history", dependencies=[Dependsrequire_permissions["ai.use"]`

## admin/automation/router.py  （4 端点）

- `- `get"`/settings",`
- `- `put"`/settings",`
- `- `get"`/logs",`
- `- `post"`/dry-run",`
- `get` `/settings", dependencies=[Dependsrequire_permissions["setting.manage"]`
- `put` `/settings", dependencies=[Dependsrequire_permissions["setting.manage"]`
- `get` `/logs", dependencies=[Dependsrequire_permissions["setting.manage"]`

## admin/cron_jobs.py  （4 端点）

- `- `get"`"`
- `- `put"`/{job_id}"`
- `- `post"`/reload"`
- `- `get"`/defaults"`
- `get` `"`
- `put` `/{job_id}"`
- `post` `/reload"`

## admin/dictionary/router.py  （5 端点）

- `- `get"`/types"`
- `- `post"`/types"`
- `- `get"`/types/{dict_type_id}/items"`
- `- `post"`/types/{dict_type_id}/items"`
- `- `delete"`/types/{dict_type_id}/items/{item_id}"`
- `get` `/types"`
- `post` `/types"`
- `get` `/types/{dict_type_id}/items"`
- `post` `/types/{dict_type_id}/items"`

## admin/equipment/router.py  （12 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `put"`/{equipment_id}"`
- `- `post"`/{equipment_id}/check"`
- `- `get"`/{equipment_id}/checks"`
- `- `get"`/maintenance-plans"`
- `- `post"`/maintenance-plans"`
- `- `put"`/maintenance-plans/{plan_id}"`
- `- `delete"`/maintenance-plans/{plan_id}"`
- `- `get"`/maintenance-logs"`
- `- `post"`/maintenance-logs"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `put` `/{equipment_id}"`
- `post` `/{equipment_id}/check"`
- `get` `/{equipment_id}/checks"`
- `get` `/maintenance-plans"`
- `post` `/maintenance-plans"`
- `put` `/maintenance-plans/{plan_id}"`
- `delete` `/maintenance-plans/{plan_id}"`
- `get` `/maintenance-logs"`

## admin/erp/accounts.py  （5 端点）

- `- `get"`"`
- `- `get"`/options"`
- `- `post"`"`
- `- `put"`/{account_id}"`
- `- `delete"`/{account_id}"`
- `get` `"`
- `get` `/options"`
- `post` `"`
- `put` `/{account_id}"`

## admin/erp/assets.py  （13 端点）

- `- `get"`"`
- `- `post"`"`
- `- `post"`/depreciate-batch"`
- `- `get"`/depreciation"`
- `- `get"`/{asset_id}/depreciation"`
- `- `post"`/checks"`
- `- `get"`/checks"`
- `- `get"`/checks/{check_id}"`
- `- `put"`/checks/{check_id}"`
- `- `post"`/checks/{check_id}/complete"`
- `- `get"`/{asset_id}"`
- `- `put"`/{asset_id}"`
- `- `delete"`/{asset_id}"`
- `get` `"`
- `post` `"`
- `post` `/depreciate-batch"`
- `get` `/depreciation"`
- `get` `/{asset_id}/depreciation"`
- `post` `/checks"`
- `get` `/checks"`
- `get` `/checks/{check_id}"`
- `put` `/checks/{check_id}"`
- `post` `/checks/{check_id}/complete"`
- `get` `/{asset_id}"`
- `put` `/{asset_id}"`

## admin/erp/costs.py  （5 端点）

- `- `get"`"`
- `- `get"`/{work_order_id}"`
- `- `post"`/calculate"`
- `- `post"`/{work_order_id}/overhead"`
- `- `post"`/{work_order_id}/close"`
- `get` `"`
- `get` `/{work_order_id}"`
- `post` `/calculate"`
- `post` `/{work_order_id}/overhead"`

## admin/erp/invoices.py  （7 端点）

- `- `get"`"`
- `- `get"`/{invoice_id}"`
- `- `post"`"`
- `- `put"`/{invoice_id}"`
- `- `delete"`/{invoice_id}"`
- `- `post"`/{invoice_id}/post"`
- `- `post"`/{invoice_id}/void"`
- `get` `"`
- `get` `/{invoice_id}"`
- `post` `"`
- `put` `/{invoice_id}"`
- `delete` `/{invoice_id}"`
- `post` `/{invoice_id}/post"`

## admin/erp/reports.py  （2 端点）

- `- `get"`/trial-balance"`
- `- `get"`/balance-sheet"`
- `get` `/trial-balance"`

## admin/erp/vouchers.py  （7 端点）

- `- `get"`"`
- `- `get"`/{voucher_id}"`
- `- `post"`"`
- `- `put"`/{voucher_id}"`
- `- `delete"`/{voucher_id}"`
- `- `post"`/{voucher_id}/post"`
- `- `post"`/{voucher_id}/unpost"`
- `get` `"`
- `get` `/{voucher_id}"`
- `post` `"`
- `put` `/{voucher_id}"`
- `delete` `/{voucher_id}"`
- `post` `/{voucher_id}/post"`

## admin/exec_dashboard/router.py  （11 端点）

- `- `get"`/summary"`
- `- `get"`/revenue"`
- `- `get"`/profit-margin"`
- `- `get"`/delivery-rate"`
- `- `get"`/collection-rate"`
- `- `get"`/capacity-utilization"`
- `- `get"`/revenue-trend"`
- `- `get"`/order-status"`
- `- `get"`/top-customers"`
- `- `get"`/top-skus"`
- `- `get"`/overdue-orders"`
- `get` `/summary"`
- `get` `/revenue"`
- `get` `/profit-margin"`
- `get` `/delivery-rate"`
- `get` `/collection-rate"`
- `get` `/capacity-utilization"`
- `get` `/revenue-trend"`
- `get` `/order-status"`
- `get` `/top-customers"`
- `get` `/top-skus"`

## admin/export_jobs.py  （1 端点）

- `- `get"`/export-jobs/{job_id}"`

## admin/finance/router.py  （13 端点）

- `- `get"`"`
- `- `get"`/ledgers"`
- `- `post"`/ledgers"`
- `- `get"`/profit"`
- `- `get"`/payables"`
- `- `post"`"`
- `- `post"`/{statement_id}/confirm"`
- `- `post"`/{statement_id}/mark-paid"`
- `- `get"`/{statement_id}/print"`
- `- `get"`/{statement_id}/print-pdf"`
- `- `post"`/statements/export"`
- `- `get"`/statements/export-jobs"`
- `- `get"`/{statement_id}"`
- `get` `"`
- `get` `/ledgers"`
- `post` `/ledgers"`
- `get` `/profit"`
- `get` `/payables"`
- `post` `"`
- `post` `/{statement_id}/confirm"`
- `post` `/{statement_id}/mark-paid"`
- `get` `/{statement_id}/print"`
- `get` `/{statement_id}/print-pdf"`
- `post` `/statements/export"`
- `get` `/statements/export-jobs"`

## admin/industry/__init__.py  （5 端点）

- `- `get"`"`
- `- `get"`/current"`
- `- `post"`/activate"`
- `- `post"`/deactivate"`
- `- `post"`/reseed"`
- `get` `"`
- `get` `/current"`
- `post` `/activate"`
- `post` `/deactivate"`

## admin/master/boms.py  （9 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/meta/form-options"`
- `- `get"`/resolve/{sku_id}"`
- `- `post"`"`
- `- `get"`/{bom_id}"`
- `- `put"`/{bom_id}"`
- `- `post"`/{bom_id}/copy-to-sku"`
- `- `delete"`/{bom_id}"`
- `get` `"`
- `get` `/export"`
- `get` `/meta/form-options"`
- `get` `/resolve/{sku_id}"`
- `post` `"`
- `get` `/{bom_id}"`
- `put` `/{bom_id}"`
- `post` `/{bom_id}/copy-to-sku"`

## admin/master/materials.py  （6 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{material_id}"`
- `- `put"`/{material_id}"`
- `- `delete"`/{material_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{material_id}"`
- `put` `/{material_id}"`

## admin/master/process_prices.py  （8 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/matrix"`
- `- `post"`/batch"`
- `- `post"`"`
- `- `get"`/{price_id}"`
- `- `put"`/{price_id}"`
- `- `delete"`/{price_id}"`
- `get` `"`
- `get` `/export"`
- `get` `/matrix"`
- `post` `/batch"`
- `post` `"`
- `get` `/{price_id}"`
- `put` `/{price_id}"`

## admin/master/process_routes.py  （5 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/{route_id}"`
- `- `put"`/{route_id}"`
- `- `delete"`/{route_id}"`
- `get` `"`
- `post` `"`
- `get` `/{route_id}"`
- `put` `/{route_id}"`

## admin/master/processes.py  （8 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{process_id}"`
- `- `put"`/{process_id}"`
- `- `delete"`/{process_id}"`
- `- `get"`/{process_id}/skills"`
- `- `put"`/{process_id}/skills"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{process_id}"`
- `put` `/{process_id}"`
- `delete` `/{process_id}"`
- `get` `/{process_id}/skills"`

## admin/master/products.py  （6 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{product_id}"`
- `- `put"`/{product_id}"`
- `- `delete"`/{product_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{product_id}"`
- `put` `/{product_id}"`

## admin/master/skus.py  （9 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/batch-template"`
- `- `post"`/batch-with-prices",`
- `- `get"`/{sku_id}"`
- `- `put"`/{sku_id}"`
- `- `delete"`/{sku_id}"`
- `- `post"`/import-excel"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/batch-template"`
- `post` `/batch-with-prices", dependencies=[Dependsrequire_permissions["price.manage"]`
- `get` `/{sku_id}"`
- `put` `/{sku_id}"`
- `delete` `/{sku_id}"`

## admin/master/suppliers.py  （6 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{supplier_id}"`
- `- `put"`/{supplier_id}"`
- `- `delete"`/{supplier_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{supplier_id}"`
- `put` `/{supplier_id}"`

## admin/mold/router.py  （11 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/overdue"`
- `- `get"`/{mold_id}"`
- `- `put"`/{mold_id}"`
- `- `delete"`/{mold_id}"`
- `- `get"`/{mold_id}/maintenance-logs"`
- `- `post"`/{mold_id}/maintenance-logs"`
- `- `get"`/{mold_id}/process-bindings"`
- `- `put"`/{mold_id}/process-bindings"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/overdue"`
- `get` `/{mold_id}"`
- `put` `/{mold_id}"`
- `delete` `/{mold_id}"`
- `get` `/{mold_id}/maintenance-logs"`
- `post` `/{mold_id}/maintenance-logs"`
- `get` `/{mold_id}/process-bindings"`

## admin/mrp/router.py  （4 端点）

- `- `post"`/run"`
- `- `get"`/runs"`
- `- `get"`/runs/{run_id}"`
- `- `post"`/runs/{run_id}/convert"`
- `post` `/run"`
- `get` `/runs"`
- `get` `/runs/{run_id}"`

## admin/production/assignments.py  （3 端点）

- `- `get"`"`
- `- `get"`/{assignment_id}/qr"`
- `- `delete"`/{assignment_id}"`
- `get` `"`
- `get` `/{assignment_id}/qr"`

## admin/production/crm.py  （62 端点）

- `- `get"`/opportunities"`
- `- `get"`/tags"`
- `- `post"`/tags"`
- `- `put"`/tags/{tag_id}"`
- `- `delete"`/tags/{tag_id}"`
- `- `get"`/public-pool/opportunities"`
- `- `post"`/public-pool/opportunities/{opportunity_id}/claim"`
- `- `post"`/public-pool/opportunities/{opportunity_id}/release"`
- `- `post"`/public-pool/recycle"`
- `- `get"`/opportunities/stats"`
- `- `get"`/settings"`
- `- `put"`/settings"`
- `- `get"`/dashboard-summary"`
- `- `get"`/after-sales"`
- `- `put"`/after-sales/{after_sale_id}"`
- `- `get"`/leads"`
- `- `post"`/leads"`
- `- `get"`/leads/{lead_id}"`
- `- `put"`/leads/{lead_id}"`
- `- `delete"`/leads/{lead_id}"`
- `- `post"`/leads/{lead_id}/convert"`
- `- `post"`/leads/{lead_id}/claim"`
- `- `post"`/leads/{lead_id}/release"`
- `- `post"`/leads/public-pool/recycle"`
- `- `get"`/leads/{lead_id}/activities"`
- `- `post"`/leads/{lead_id}/activities"`
- `- `get"`/leads/stats/summary"`
- `- `get"`/quotations"`
- `- `post"`/quotations"`
- `- `get"`/quotations/{quotation_id}"`
- `- `put"`/quotations/{quotation_id}"`
- `- `post"`/quotations/{quotation_id}/new-version"`
- `- `post"`/quotations/{quotation_id}/send"`
- `- `post"`/quotations/{quotation_id}/reject"`
- `- `post"`/quotations/{quotation_id}/convert-to-order"`
- `- `get"`/contracts"`
- `- `post"`/contracts"`
- `- `get"`/contracts/{contract_id}"`
- `- `put"`/contracts/{contract_id}"`
- `- `post"`/contracts/{contract_id}/renew"`
- `- `post"`/contracts/{contract_id}/terminate"`
- `- `post"`/contracts/{contract_id}/payment-plans/{plan_id}/record"`
- `- `get"`/win-loss-reasons"`
- `- `post"`/win-loss-reasons"`
- `- `put"`/win-loss-reasons/{reason_id}"`
- `- `delete"`/win-loss-reasons/{reason_id}"`
- `- `get"`/campaigns"`
- `- `post"`/campaigns"`
- `- `get"`/campaigns/{campaign_id}"`
- `- `put"`/campaigns/{campaign_id}"`
- `- `post"`/campaigns/{campaign_id}/members"`
- `- `get"`/campaigns/{campaign_id}/members"`
- `- `delete"`/campaigns/{campaign_id}/members/{member_type}/{member_id}"`
- `- `post"`/campaigns/{campaign_id}/recalculate-roi"`
- `- `get"`/sales-targets"`
- `- `post"`/sales-targets"`
- `- `get"`/sales-targets/{target_id}"`
- `- `put"`/sales-targets/{target_id}"`
- `- `delete"`/sales-targets/{target_id}"`
- `- `get"`/dashboard/sales-targets"`
- `- `get"`/customers/{customer_id}/contracts"`
- `- `get"`/customers/{customer_id}/quotations"`
- `get` `/opportunities"`
- `get` `/tags"`
- `post` `/tags"`
- `put` `/tags/{tag_id}"`
- `delete` `/tags/{tag_id}"`
- `get` `/public-pool/opportunities"`
- `post` `/public-pool/opportunities/{opportunity_id}/claim"`
- `post` `/public-pool/opportunities/{opportunity_id}/release"`
- `post` `/public-pool/recycle"`
- `get` `/opportunities/stats"`
- `get` `/settings"`
- `put` `/settings"`
- `get` `/dashboard-summary"`
- `get` `/after-sales"`
- `put` `/after-sales/{after_sale_id}"`
- `get` `/leads"`
- `post` `/leads"`
- `get` `/leads/{lead_id}"`
- `put` `/leads/{lead_id}"`
- `delete` `/leads/{lead_id}"`
- `post` `/leads/{lead_id}/convert"`
- `post` `/leads/{lead_id}/claim"`
- `post` `/leads/{lead_id}/release"`
- `post` `/leads/public-pool/recycle"`
- `get` `/leads/{lead_id}/activities"`
- `post` `/leads/{lead_id}/activities"`
- `get` `/leads/stats/summary"`
- `get` `/quotations"`
- `post` `/quotations"`
- `get` `/quotations/{quotation_id}"`
- `put` `/quotations/{quotation_id}"`
- `post` `/quotations/{quotation_id}/new-version"`
- `post` `/quotations/{quotation_id}/send"`
- `post` `/quotations/{quotation_id}/reject"`
- `post` `/quotations/{quotation_id}/convert-to-order"`
- `get` `/contracts"`
- `post` `/contracts"`
- `get` `/contracts/{contract_id}"`
- `put` `/contracts/{contract_id}"`
- `post` `/contracts/{contract_id}/renew"`
- `post` `/contracts/{contract_id}/terminate"`
- `post` `/contracts/{contract_id}/payment-plans/{plan_id}/record"`
- `get` `/win-loss-reasons"`
- `post` `/win-loss-reasons"`
- `put` `/win-loss-reasons/{reason_id}"`
- `delete` `/win-loss-reasons/{reason_id}"`
- `get` `/campaigns"`
- `post` `/campaigns"`
- `get` `/campaigns/{campaign_id}"`
- `put` `/campaigns/{campaign_id}"`
- `post` `/campaigns/{campaign_id}/members"`
- `get` `/campaigns/{campaign_id}/members"`
- `delete` `/campaigns/{campaign_id}/members/{member_type}/{member_id}"`
- `post` `/campaigns/{campaign_id}/recalculate-roi"`
- `get` `/sales-targets"`
- `post` `/sales-targets"`
- `get` `/sales-targets/{target_id}"`
- `put` `/sales-targets/{target_id}"`
- `delete` `/sales-targets/{target_id}"`
- `get` `/dashboard/sales-targets"`
- `get` `/customers/{customer_id}/contracts"`

## admin/production/customers.py  （23 端点）

- `- `get"`"`
- `- `get"`/{customer_id}"`
- `- `get"`/{customer_id}/products"`
- `- `put"`/{customer_id}/products"`
- `- `post"`"`
- `- `put"`/{customer_id}"`
- `- `get"`/{customer_id}/contacts"`
- `- `post"`/{customer_id}/contacts"`
- `- `put"`/{customer_id}/contacts/{contact_id}"`
- `- `delete"`/{customer_id}/contacts/{contact_id}"`
- `- `get"`/{customer_id}/opportunities"`
- `- `post"`/{customer_id}/opportunities"`
- `- `put"`/{customer_id}/opportunities/{opportunity_id}"`
- `- `delete"`/{customer_id}/opportunities/{opportunity_id}"`
- `- `get"`/{customer_id}/opportunities/{opportunity_id}/activities"`
- `- `post"`/{customer_id}/opportunities/{opportunity_id}/activities"`
- `- `post"`/{customer_id}/opportunities/{opportunity_id}/convert-to-order"`
- `- `get"`/{customer_id}/tags"`
- `- `put"`/{customer_id}/tags"`
- `- `get"`/{customer_id}/profile"`
- `- `post"`/{customer_id}/profile/recalculate"`
- `- `post"`/{customer_id}/leads/convert"`
- `- `get"`/suggest/{customer_id}"`
- `get` `"`
- `get` `/{customer_id}"`
- `get` `/{customer_id}/products"`
- `put` `/{customer_id}/products"`
- `post` `"`
- `put` `/{customer_id}"`
- `get` `/{customer_id}/contacts"`
- `post` `/{customer_id}/contacts"`
- `put` `/{customer_id}/contacts/{contact_id}"`
- `delete` `/{customer_id}/contacts/{contact_id}"`
- `get` `/{customer_id}/opportunities"`
- `post` `/{customer_id}/opportunities"`
- `put` `/{customer_id}/opportunities/{opportunity_id}"`
- `delete` `/{customer_id}/opportunities/{opportunity_id}"`
- `get` `/{customer_id}/opportunities/{opportunity_id}/activities"`
- `post` `/{customer_id}/opportunities/{opportunity_id}/activities"`
- `post` `/{customer_id}/opportunities/{opportunity_id}/convert-to-order"`
- `get` `/{customer_id}/tags"`
- `put` `/{customer_id}/tags"`
- `get` `/{customer_id}/profile"`
- `post` `/{customer_id}/profile/recalculate"`
- `post` `/{customer_id}/leads/convert"`

## admin/production/orders.py  （13 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/import-template"`
- `- `post"`/import-excel"`
- `- `get"`/meta/form-options"`
- `- `get"`/{order_id}"`
- `- `post"`"`
- `- `delete"`/{order_id}"`
- `- `put"`/{order_id}"`
- `- `post"`/{order_id}/reject"`
- `- `post"`/{order_id}/confirm"`
- `- `get"`/{order_id}/print"`
- `- `get"`/{order_id}/print-pdf"`
- `get` `"`
- `get` `/export"`
- `get` `/import-template"`
- `post` `/import-excel"`
- `get` `/meta/form-options"`
- `get` `/{order_id}"`
- `post` `"`
- `delete` `/{order_id}"`
- `put` `/{order_id}"`
- `post` `/{order_id}/reject"`
- `post` `/{order_id}/confirm"`
- `get` `/{order_id}/print"`

## admin/production/plans.py  （32 端点）

- `- `get"`/plans/capacity"`
- `- `put"`/plans/capacity/unit"`
- `- `put"`/plans/capacity"`
- `- `get"`/plans/capacity/workshops"`
- `- `put"`/plans/capacity/workshops"`
- `- `get"`/plans/capacity/users"`
- `- `get"`/plans/capacity/user-rows"`
- `- `put"`/plans/capacity/users"`
- `- `get"`/plans/capacity/equipments"`
- `- `put"`/plans/capacity/equipments"`
- `- `get"`/plans/calendar"`
- `- `put"`/plans/calendar/day"`
- `- `delete"`/plans/calendar/day"`
- `- `get"`/plans/load"`
- `- `get"`/plans/load/detail"`
- `- `post"`/plans/{plan_id}/auto-schedule"`
- `- `post"`/plans/{plan_id}/auto-dispatch"`
- `- `get"`/plans/meta/form-options"`
- `- `get"`/plans"`
- `- `post"`/plans"`
- `- `post"`/plans/{plan_id}/release"`
- `- `get"`/plans/{plan_id}"`
- `- `put"`/plans/{plan_id}"`
- `- `get"`/plans/readiness/preview"`
- `- `get"`/plans/{plan_id}/readiness"`
- `- `get"`/plans/{plan_id}/kitting"`
- `- `post"`/plans/{plan_id}/kitting/create-purchase",`
- `- `get"`/plans/{plan_id}/kitting/purchase-orders"`
- `- `get"`/plans/{plan_id}/forecast"`
- `- `get"`/plans/{plan_id}/aps-strategy",`
- `- `get"`/plans/{plan_id}/forecast"`
- `- `get"`/plans/{plan_id}/aps-strategy",`
- `get` `/plans/capacity"`
- `put` `/plans/capacity/unit"`
- `put` `/plans/capacity"`
- `get` `/plans/capacity/workshops"`
- `put` `/plans/capacity/workshops"`
- `get` `/plans/capacity/users"`
- `get` `/plans/capacity/user-rows"`
- `put` `/plans/capacity/users"`
- `get` `/plans/capacity/equipments"`
- `put` `/plans/capacity/equipments"`
- `get` `/plans/calendar"`
- `put` `/plans/calendar/day"`
- `delete` `/plans/calendar/day"`
- `get` `/plans/load"`
- `get` `/plans/load/detail"`
- `post` `/plans/{plan_id}/auto-schedule"`
- `post` `/plans/{plan_id}/auto-dispatch"`
- `get` `/plans/meta/form-options"`
- `get` `/plans"`
- `post` `/plans"`
- `post` `/plans/{plan_id}/release"`
- `get` `/plans/{plan_id}"`
- `put` `/plans/{plan_id}"`
- `get` `/plans/readiness/preview"`
- `get` `/plans/{plan_id}/readiness"`
- `get` `/plans/{plan_id}/kitting"`
- `post` `/plans/{plan_id}/kitting/create-purchase", dependencies=[Dependsrequire_permissions["purchase.manage"]`
- `get` `/plans/{plan_id}/kitting/purchase-orders"`
- `get` `/plans/{plan_id}/forecast"`
- `get` `/plans/{plan_id}/aps-strategy", dependencies=[Dependsrequire_permissions["ai.use", "plan.manage"]`
- `get` `/plans/{plan_id}/forecast"`

## admin/production/quality.py  （10 端点）

- `- `get"`/inspection-templates"`
- `- `get"`/inspection-templates/{template_id}"`
- `- `post"`/inspection-templates"`
- `- `put"`/inspection-templates/{template_id}"`
- `- `delete"`/inspection-templates/{template_id}"`
- `- `get"`/defect-codes"`
- `- `get"`/defect-codes/export"`
- `- `post"`/defect-codes"`
- `- `put"`/defect-codes/{code_id}"`
- `- `delete"`/defect-codes/{code_id}"`
- `get` `/inspection-templates"`
- `get` `/inspection-templates/{template_id}"`
- `post` `/inspection-templates"`
- `put` `/inspection-templates/{template_id}"`
- `delete` `/inspection-templates/{template_id}"`
- `get` `/defect-codes"`
- `get` `/defect-codes/export"`
- `post` `/defect-codes"`
- `put` `/defect-codes/{code_id}"`

## admin/production/report_units.py  （6 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/approval-steps"`
- `- `get"`/{unit_id}"`
- `- `post"`/{unit_id}/approve"`
- `- `post"`/{unit_id}/reject"`
- `get` `"`
- `get` `/export"`
- `get` `/approval-steps"`
- `get` `/{unit_id}"`
- `post` `/{unit_id}/approve"`

## admin/production/reports.py  （9 端点）

- `- `get"`"`
- `- `get"`/{report_id}"`
- `- `post"`/{report_id}/leader-approve"`
- `- `post"`/{report_id}/qc-approve"`
- `- `post"`/{report_id}/reject"`
- `- `get"`/salary/items"`
- `- `get"`/salary/allowances"`
- `- `post"`/salary/allowances"`
- `- `get"`/salary/summary"`
- `get` `"`
- `get` `/{report_id}"`
- `post` `/{report_id}/leader-approve"`
- `post` `/{report_id}/qc-approve"`
- `post` `/{report_id}/reject"`
- `get` `/salary/items"`
- `get` `/salary/allowances"`
- `post` `/salary/allowances"`

## admin/production/salary_reports.py  （13 端点）

- `- `get"`/salary/ledger"`
- `- `get"`/salary/export"`
- `- `post"`/salary/export-jobs"`
- `- `get"`/salary/export-jobs/{job_id}"`
- `- `get"`/salary/export-jobs"`
- `- `get"`/salary/slips"`
- `- `get"`/salary/slips/export"`
- `- `post"`/salary/slips/{slip_id}/reset-confirm"`
- `- `post"`/salary/slips/remind"`
- `- `get"`/salary/hourly-items"`
- `- `post"`/salary/generate-time-items"`
- `- `get"`/salary/hourly-summary"`
- `- `get"`/salary/hourly-ledger"`
- `get` `/salary/ledger"`
- `get` `/salary/export"`
- `post` `/salary/export-jobs"`
- `get` `/salary/export-jobs/{job_id}"`
- `get` `/salary/export-jobs"`
- `get` `/salary/slips"`
- `get` `/salary/slips/export"`
- `post` `/salary/slips/{slip_id}/reset-confirm"`
- `post` `/salary/slips/remind"`
- `get` `/salary/hourly-items"`
- `post` `/salary/generate-time-items"`
- `get` `/salary/hourly-summary"`

## admin/production/tasks.py  （10 端点）

- `- `get"`"`
- `- `get"`/dispatch-skills",`
- `- `get"`/dispatch-users",`
- `- `get"`/{task_id}/print-label",`
- `- `post"`/print-label-batch",`
- `- `get"`/{task_id}/print-label-pdf",`
- `- `get"`/{task_id}/assignments",`
- `- `put"`/{task_id}/assignments",`
- `- `post"`/{task_id}/assign",`
- `- `get"`/{task_id}"`
- `get` `"`
- `get` `/dispatch-skills", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `get` `/dispatch-users", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `get` `/{task_id}/print-label", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `post` `/print-label-batch", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `get` `/{task_id}/print-label-pdf", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `get` `/{task_id}/assignments", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `put` `/{task_id}/assignments", dependencies=[Dependsrequire_permissions["dispatch.manage"]`
- `post` `/{task_id}/assign", dependencies=[Dependsrequire_permissions["dispatch.manage"]`

## admin/production/temp_reports.py  （2 端点）

- `- `get"`/temp-reports"`
- `- `post"`/temp-reports/{temp_report_id}/bind"`
- `get` `/temp-reports"`

## admin/production/work_orders.py  （5 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/{work_order_id}"`
- `- `get"`/{work_order_id}/print-product-labels"`
- `- `post"`/{work_order_id}/print-product-labels"`
- `get` `"`
- `get` `/export"`
- `get` `/{work_order_id}"`
- `get` `/{work_order_id}/print-product-labels"`

## admin/purchase/orders.py  （11 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{order_id}"`
- `- `post"`/{order_id}/confirm"`
- `- `post"`/{order_id}/receive"`
- `- `post"`/{order_id}/return"`
- `- `get"`/{order_id}/batches"`
- `- `post"`/{order_id}/cancel"`
- `- `get"`/{order_id}/print"`
- `- `get"`/{order_id}/print-pdf"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{order_id}"`
- `post` `/{order_id}/confirm"`
- `post` `/{order_id}/receive"`
- `post` `/{order_id}/return"`
- `get` `/{order_id}/batches"`
- `post` `/{order_id}/cancel"`
- `get` `/{order_id}/print"`

## admin/purchase/statements.py  （9 端点）

- `- `get"`"`
- `- `post"`"`
- `- `post"`/export"`
- `- `get"`/export-jobs"`
- `- `get"`/{statement_id}"`
- `- `get"`/{statement_id}/print"`
- `- `get"`/{statement_id}/print-pdf"`
- `- `post"`/{statement_id}/confirm"`
- `- `post"`/{statement_id}/mark-paid"`
- `get` `"`
- `post` `"`
- `post` `/export"`
- `get` `/export-jobs"`
- `get` `/{statement_id}"`
- `get` `/{statement_id}/print"`
- `get` `/{statement_id}/print-pdf"`
- `post` `/{statement_id}/confirm"`

## admin/quotation/router.py  （9 端点）

- `- `get"`"`
- `- `get"`/{qid}"`
- `- `post"`"`
- `- `put"`/{qid}"`
- `- `post"`/{qid}/items"`
- `- `post"`/{qid}/submit"`
- `- `post"`/{qid}/approve"`
- `- `post"`/{qid}/reject"`
- `- `post"`/{qid}/convert"`
- `get` `"`
- `get` `/{qid}"`
- `post` `"`
- `put` `/{qid}"`
- `post` `/{qid}/items"`
- `post` `/{qid}/submit"`
- `post` `/{qid}/approve"`
- `post` `/{qid}/reject"`

## admin/reports/purchase.py  （1 端点）

- `- `get"`/purchase"`

## admin/reports/router.py  （8 端点）

- `- `get"`/defect-pareto"`
- `- `get"`/production"`
- `- `get"`/yield"`
- `- `get"`/process-rank"`
- `- `get"`/daily-trend"`
- `- `post"`/export/production"`
- `- `post"`/export/yield"`
- `- `get"`/export-jobs"`
- `get` `/defect-pareto"`
- `get` `/production"`
- `get` `/yield"`
- `get` `/process-rank"`
- `get` `/daily-trend"`
- `post` `/export/production"`
- `post` `/export/yield"`

## admin/shift/router.py  （9 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `put"`/{shift_id}"`
- `- `delete"`/{shift_id}"`
- `- `get"`/schedules"`
- `- `post"`/schedules"`
- `- `post"`/schedules/batch"`
- `- `delete"`/schedules/{schedule_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `put` `/{shift_id}"`
- `delete` `/{shift_id}"`
- `get` `/schedules"`
- `post` `/schedules"`
- `post` `/schedules/batch"`

## admin/spc/router.py  （8 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/{chart_id}"`
- `- `put"`/{chart_id}"`
- `- `delete"`/{chart_id}"`
- `- `get"`/{chart_id}/samples"`
- `- `post"`/{chart_id}/samples"`
- `- `get"`/{chart_id}/calculate"`
- `get` `"`
- `post` `"`
- `get` `/{chart_id}"`
- `put` `/{chart_id}"`
- `delete` `/{chart_id}"`
- `get` `/{chart_id}/samples"`
- `post` `/{chart_id}/samples"`

## admin/subcontract/router.py  （12 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `get"`/{oid}"`
- `- `get"`/{oid}/print"`
- `- `get"`/{oid}/print-pdf"`
- `- `post"`"`
- `- `post"`/{oid}/items"`
- `- `post"`/{oid}/send"`
- `- `post"`/{oid}/receive"`
- `- `post"`/{oid}/settle"`
- `- `get"`/{oid}/send-logs"`
- `- `get"`/{oid}/receive-logs"`
- `get` `"`
- `get` `/export"`
- `get` `/{oid}"`
- `get` `/{oid}/print"`
- `get` `/{oid}/print-pdf"`
- `post` `"`
- `post` `/{oid}/items"`
- `post` `/{oid}/send"`
- `post` `/{oid}/receive"`
- `post` `/{oid}/settle"`
- `get` `/{oid}/send-logs"`

## admin/system/attachments.py  （5 端点）

- `- `get"`"`
- `- `post"`/upload"`
- `- `get"`/{attachment_id}"`
- `- `get"`/{attachment_id}/url"`
- `- `delete"`/{attachment_id}"`
- `get` `"`
- `post` `/upload"`
- `get` `/{attachment_id}"`
- `get` `/{attachment_id}/url"`

## admin/system/attendance_records.py  （5 端点）

- `- `get"`"`
- `- `post"`"`
- `- `put"`/{record_id}"`
- `- `get"`/geofence"`
- `- `put"`/geofence"`
- `get` `"`
- `post` `"`
- `put` `/{record_id}"`
- `get` `/geofence"`

## admin/system/codes.py  （2 端点）

- `- `get"`/types"`
- `- `get"`/next"`
- `get` `/types"`

## admin/system/demo_data.py  （3 端点）

- `- `get"`/status"`
- `- `post"`/install"`
- `- `post"`/uninstall"`
- `get` `/status"`
- `post` `/install"`

## admin/system/departments.py  （5 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/{department_id}"`
- `- `put"`/{department_id}"`
- `- `delete"`/{department_id}"`
- `get` `"`
- `post` `"`
- `get` `/{department_id}"`
- `put` `/{department_id}"`

## admin/system/dingtalk.py  （16 端点）

- `- `get"`/dingtalk"`
- `- `put"`/dingtalk"`
- `- `post"`/dingtalk/test-connection"`
- `- `post"`/dingtalk/test-send"`
- `- `get"`/dingtalk/setup-checklist"`
- `- `get"`/dingtalk/push-logs"`
- `- `post"`/dingtalk/push-logs/{log_id}/retry"`
- `- `get"`/dingtalk/user-bindings"`
- `- `put"`/dingtalk/user-bindings/{user_id}"`
- `- `post"`/dingtalk/user-bindings/batch-match-mobile"`
- `- `get"`/dingtalk/department-bindings"`
- `- `put"`/dingtalk/department-bindings/{department_id}"`
- `- `get"`/dingtalk/dingtalk-departments"`
- `- `get"`/dingtalk/delivery-diagnostics"`
- `- `post"`/dingtalk/bind-url"`
- `- `post"`/dingtalk/simulate"`
- `get` `/dingtalk"`
- `put` `/dingtalk"`
- `post` `/dingtalk/test-connection"`
- `post` `/dingtalk/test-send"`
- `get` `/dingtalk/setup-checklist"`
- `get` `/dingtalk/push-logs"`
- `post` `/dingtalk/push-logs/{log_id}/retry"`
- `get` `/dingtalk/user-bindings"`
- `put` `/dingtalk/user-bindings/{user_id}"`
- `post` `/dingtalk/user-bindings/batch-match-mobile"`
- `get` `/dingtalk/department-bindings"`
- `put` `/dingtalk/department-bindings/{department_id}"`
- `get` `/dingtalk/dingtalk-departments"`
- `get` `/dingtalk/delivery-diagnostics"`
- `post` `/dingtalk/bind-url"`

## admin/system/feishu.py  （18 端点）

- `- `get"`/feishu"`
- `- `put"`/feishu"`
- `- `post"`/feishu/test-connection"`
- `- `post"`/feishu/test-send"`
- `- `get"`/feishu/chats"`
- `- `post"`/feishu/simulate"`
- `- `get"`/feishu/push-logs"`
- `- `post"`/feishu/push-logs/{log_id}/retry"`
- `- `get"`/feishu/user-bindings"`
- `- `put"`/feishu/user-bindings/{user_id}"`
- `- `post"`/feishu/user-bindings/batch-match-mobile"`
- `- `get"`/feishu/department-bindings"`
- `- `put"`/feishu/department-bindings/{department_id}"`
- `- `get"`/feishu/feishu-departments"`
- `- `get"`/feishu/setup-checklist"`
- `- `get"`/feishu/delivery-diagnostics"`
- `- `post"`/feishu/bind-url"`
- `- `post"`/feishu/preview-card"`
- `get` `/feishu"`
- `put` `/feishu"`
- `post` `/feishu/test-connection"`
- `post` `/feishu/test-send"`
- `get` `/feishu/chats"`
- `post` `/feishu/simulate"`
- `get` `/feishu/push-logs"`
- `post` `/feishu/push-logs/{log_id}/retry"`
- `get` `/feishu/user-bindings"`
- `put` `/feishu/user-bindings/{user_id}"`
- `post` `/feishu/user-bindings/batch-match-mobile"`
- `get` `/feishu/department-bindings"`
- `put` `/feishu/department-bindings/{department_id}"`
- `get` `/feishu/feishu-departments"`
- `get` `/feishu/setup-checklist"`
- `get` `/feishu/delivery-diagnostics"`
- `post` `/feishu/bind-url"`

## admin/system/invites.py  （2 端点）

- `- `get"`"`
- `- `post"`"`
- `get` `"`

## admin/system/message_center.py  （11 端点）

- `- `get"`/overview"`
- `- `get"`/groups"`
- `- `put"`/groups"`
- `- `post"`/groups"`
- `- `get"`/rules"`
- `- `get"`/user-bindings"`
- `- `get"`/push-logs"`
- `- `get"`/alert-recipients"`
- `- `put"`/alert-recipients"`
- `- `post"`/run-migration"`
- `- `get"`/all-bindable-users"`
- `get` `/overview"`
- `get` `/groups"`
- `put` `/groups"`
- `post` `/groups"`
- `get` `/rules"`
- `get` `/user-bindings"`
- `get` `/push-logs"`
- `get` `/alert-recipients"`
- `put` `/alert-recipients"`
- `post` `/run-migration"`

## admin/system/notifications.py  （4 端点）

- `- `get"`"`
- `- `post"`/read"`
- `- `post"`/read-all"`
- `- `get"`/unread-count"`
- `get` `"`
- `post` `/read"`
- `post` `/read-all"`

## admin/system/operation_logs.py  （1 端点）

- `- `get"`"`

## admin/system/permissions.py  （4 端点）

- `- `get"`"`
- `- `post"`"`
- `- `put"`/{permission_id}"`
- `- `delete"`/{permission_id}"`
- `get` `"`
- `post` `"`
- `put` `/{permission_id}"`

## admin/system/print_templates.py  （7 端点）

- `- `get"`"`
- `- `post"`"`
- `- `get"`/{template_id}"`
- `- `put"`/{template_id}"`
- `- `delete"`/{template_id}"`
- `- `post"`/{template_id}/render"`
- `- `post"`/{template_id}/render-pdf"`
- `get` `"`
- `post` `"`
- `get` `/{template_id}"`
- `put` `/{template_id}"`
- `delete` `/{template_id}"`
- `post` `/{template_id}/render"`

## admin/system/report_media.py  （2 端点）

- `- `get"`/report-media"`
- `- `put"`/report-media"`
- `get` `/report-media"`

## admin/system/report_mode.py  （2 端点）

- `- `get"`/report-mode"`
- `- `put"`/report-mode"`
- `get` `/report-mode"`

## admin/system/roles.py  （7 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{role_id}"`
- `- `put"`/{role_id}"`
- `- `put"`/{role_id}/permissions"`
- `- `delete"`/{role_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{role_id}"`
- `put` `/{role_id}"`
- `put` `/{role_id}/permissions"`

## admin/system/settings.py  （4 端点）

- `- `get"`"`
- `- `get"`/{key}"`
- `- `put"`/{key}"`
- `- `delete"`/{key}"`
- `get` `"`
- `get` `/{key}"`
- `put` `/{key}"`

## admin/system/skills.py  （7 端点）

- `- `get"`"`
- `- `post"`"`
- `- `put"`/{skill_id}"`
- `- `delete"`/{skill_id}"`
- `- `get"`/users"`
- `- `get"`/users/{user_id}/skills"`
- `- `put"`/users/{user_id}/skills"`
- `get` `"`
- `post` `"`
- `put` `/{skill_id}"`
- `delete` `/{skill_id}"`
- `get` `/users"`
- `get` `/users/{user_id}/skills"`

## admin/system/users.py  （6 端点）

- `- `get"`"`
- `- `get"`/export"`
- `- `post"`"`
- `- `get"`/{user_id}"`
- `- `put"`/{user_id}"`
- `- `delete"`/{user_id}"`
- `get` `"`
- `get` `/export"`
- `post` `"`
- `get` `/{user_id}"`
- `put` `/{user_id}"`

## admin/system/version.py  （2 端点）

- `- `get"`/version"`
- `- `get"`/version/history"`
- `get` `/version"`

## admin/system/wechat_miniapp.py  （2 端点）

- `- `get"`/wechat-miniapp"`
- `- `put"`/wechat-miniapp"`
- `get` `/wechat-miniapp"`

## admin/system/wechat_mp.py  （6 端点）

- `- `get"`/wechat-mp"`
- `- `put"`/wechat-mp"`
- `- `post"`/wechat-mp/test-connection"`
- `- `post"`/wechat-mp/test-send"`
- `- `get"`/wechat-mp/push-logs"`
- `- `post"`/wechat-mp/push-logs/{log_id}/retry"`
- `get` `/wechat-mp"`
- `put` `/wechat-mp"`
- `post` `/wechat-mp/test-connection"`
- `post` `/wechat-mp/test-send"`
- `get` `/wechat-mp/push-logs"`

## admin/system/wecom.py  （15 端点）

- `- `get"`/wecom"`
- `- `put"`/wecom"`
- `- `post"`/wecom/test-connection"`
- `- `post"`/wecom/test-send"`
- `- `get"`/wecom/setup-checklist"`
- `- `get"`/wecom/push-logs"`
- `- `post"`/wecom/push-logs/{log_id}/retry"`
- `- `get"`/wecom/user-bindings"`
- `- `put"`/wecom/user-bindings/{user_id}"`
- `- `post"`/wecom/user-bindings/batch-match-mobile"`
- `- `get"`/wecom/department-bindings"`
- `- `put"`/wecom/department-bindings/{department_id}"`
- `- `get"`/wecom/wecom-departments"`
- `- `get"`/wecom/delivery-diagnostics"`
- `- `post"`/wecom/simulate"`
- `get` `/wecom"`
- `put` `/wecom"`
- `post` `/wecom/test-connection"`
- `post` `/wecom/test-send"`
- `get` `/wecom/setup-checklist"`
- `get` `/wecom/push-logs"`
- `post` `/wecom/push-logs/{log_id}/retry"`
- `get` `/wecom/user-bindings"`
- `put` `/wecom/user-bindings/{user_id}"`
- `post` `/wecom/user-bindings/batch-match-mobile"`
- `get` `/wecom/department-bindings"`
- `put` `/wecom/department-bindings/{department_id}"`
- `get` `/wecom/wecom-departments"`
- `get` `/wecom/delivery-diagnostics"`

## admin/trace/router.py  （2 端点）

- `- `get"`"`
- `- `get"`/{code}"`
- `get` `"`

## admin/warehouse/material_issues.py  （10 端点）

- `- `get"`/issues"`
- `- `get"`/issues/{issue_id}"`
- `- `post"`/issues"`
- `- `post"`/issues/{issue_id}/issue"`
- `- `post"`/issues/{issue_id}/cancel"`
- `- `get"`/returns"`
- `- `get"`/returns/{return_id}"`
- `- `post"`/returns"`
- `- `post"`/returns/{return_id}/confirm"`
- `- `post"`/returns/{return_id}/cancel"`
- `get` `/issues"`
- `get` `/issues/{issue_id}"`
- `post` `/issues"`
- `post` `/issues/{issue_id}/issue"`
- `post` `/issues/{issue_id}/cancel"`
- `get` `/returns"`
- `get` `/returns/{return_id}"`
- `post` `/returns"`
- `post` `/returns/{return_id}/confirm"`

## admin/warehouse/router.py  （9 端点）

- `- `get"`/warehouses"`
- `- `get"`/warehouses/export"`
- `- `post"`/warehouses"`
- `- `put"`/warehouses/{warehouse_id}"`
- `- `get"`/stocks"`
- `- `post"`/stocks/adjust"`
- `- `get"`/logs"`
- `- `post"`/stocks/export"`
- `- `get"`/export-jobs"`
- `get` `/warehouses"`
- `get` `/warehouses/export"`
- `post` `/warehouses"`
- `put` `/warehouses/{warehouse_id}"`
- `get` `/stocks"`
- `post` `/stocks/adjust"`
- `get` `/logs"`
- `post` `/stocks/export"`

## admin/warehouse/shipments.py  （5 端点）

- `- `get"`"`
- `- `get"`/{shipment_id}"`
- `- `post"`"`
- `- `post"`/{shipment_id}/ship"`
- `- `post"`/{shipment_id}/sign"`
- `get` `"`
- `get` `/{shipment_id}"`
- `post` `"`
- `post` `/{shipment_id}/ship"`

## admin/warehouse/warehouse_entries.py  （5 端点）

- `- `get"`/entries"`
- `- `get"`/entries/{entry_id}"`
- `- `post"`/entries"`
- `- `post"`/entries/{entry_id}/confirm"`
- `- `post"`/entries/{entry_id}/cancel"`
- `get` `/entries"`
- `get` `/entries/{entry_id}"`
- `post` `/entries"`
- `post` `/entries/{entry_id}/confirm"`

## admin/workflow/router.py  （9 端点）

- `- `post"`/start"`
- `- `get"`/todo"`
- `- `get"`/done"`
- `- `get"`/instance/{instance_id}"`
- `- `get"`/instance/{instance_id}/trace"`
- `- `post"`/task/{task_id}/approve"`
- `- `post"`/task/{task_id}/reject"`
- `- `post"`/task/{task_id}/transfer"`
- `- `post"`/instance/{instance_id}/cancel"`
- `post` `/start"`
- `get` `/todo"`
- `get` `/done"`
- `get` `/instance/{instance_id}"`
- `get` `/instance/{instance_id}/trace"`
- `post` `/task/{task_id}/approve"`
- `post` `/task/{task_id}/reject"`
- `post` `/task/{task_id}/transfer"`

## dashboard/router.py  （5 端点）

- `- `get"`/summary"`
- `- `get"`/kanban/orders"`
- `- `get"`/kanban/orders/{order_id}"`
- `- `get"`/charts"`
- `- `get"`/push-stats"`
- `get` `/summary"`
- `get` `/kanban/orders"`
- `get` `/kanban/orders/{order_id}"`
- `get` `/charts"`

## dingtalk/router.py  （3 端点）

- `- `get"`/oauth/callback"`
- `- `get"`/card-action"`
- `- `post"`/robot-message"`
- `get` `/oauth/callback"`
- `get` `/card-action"`

## feishu/router.py  （2 端点）

- `- `post"`/events"`
- `- `get"`/oauth/callback"`
- `post` `/events"`

## h5/ai.py  （15 端点）

- `- `post"`/report/check",`
- `- `post"`/report/photo-count",`
- `- `post"`/report/voice-parse",`
- `- `post"`/report/defect-classify",`
- `- `post"`/report/shift-summary",`
- `- `get"`/report/recommend",`
- `- `post"`/help"`
- `- `get"`/help/search"`
- `- `post"`/chat",`
- `- `get"`/alerts",`
- `- `post"`/alerts/run",`
- `- `get"`/models"`
- `- `get"`/conversations",`
- `- `post"`/conversations/{conversation_id}/delete",`
- `- `get"`/brief",`
- `post` `/report/check", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `post` `/report/photo-count", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `post` `/report/voice-parse", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `post` `/report/defect-classify", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `post` `/report/shift-summary", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `get` `/report/recommend", dependencies=[Dependsrequire_permissions["ai.report_assist"]`
- `post` `/help"`
- `get` `/help/search"`
- `post` `/chat", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/alerts", dependencies=[Dependsrequire_permissions["ai.alert.view"]`
- `post` `/alerts/run", dependencies=[Dependsrequire_permissions["ai.use"]`
- `get` `/models"`
- `get` `/conversations", dependencies=[Dependsrequire_permissions["ai.use"]`
- `post` `/conversations/{conversation_id}/delete", dependencies=[Dependsrequire_permissions["ai.use"]`

## h5/ai_employee/router.py  （5 端点）

- `- `get"`"`
- `- `post"`/{employee_id}/chat"`
- `- `post"`/{employee_id}/chat/stream"`
- `- `get"`/{employee_id}/conversations"`
- `- `delete"`/conversations/{conversation_id}"`
- `get` `"`
- `post` `/{employee_id}/chat"`
- `post` `/{employee_id}/chat/stream"`
- `get` `/{employee_id}/conversations"`

## h5/attendance.py  （4 端点）

- `- `post"`/check-in"`
- `- `post"`/check-out"`
- `- `get"`/records"`
- `- `get"`/geofence"`
- `post` `/check-in"`
- `post` `/check-out"`
- `get` `/records"`

## h5/customer.py  （15 端点）

- `- `get"`/catalog"`
- `- `post"`/orders"`
- `- `post"`/orders/legacy"`
- `- `post"`/orders/{order_id}/submit"`
- `- `get"`/orders"`
- `- `get"`/orders/{order_id}"`
- `- `get"`/orders/{order_id}/progress"`
- `- `get"`/statements"`
- `- `get"`/statements/{statement_id}"`
- `- `post"`/statements/{statement_id}/ack"`
- `- `post"`/statements/{statement_id}/mark-paid"`
- `- `get"`/statements/{statement_id}/download"`
- `- `get"`/orders/{order_id}/shipments"`
- `- `get"`/orders/{order_id}/after-sales"`
- `- `post"`/orders/{order_id}/after-sales"`
- `get` `/catalog"`
- `post` `/orders"`
- `post` `/orders/legacy"`
- `post` `/orders/{order_id}/submit"`
- `get` `/orders"`
- `get` `/orders/{order_id}"`
- `get` `/orders/{order_id}/progress"`
- `get` `/statements"`
- `get` `/statements/{statement_id}"`
- `post` `/statements/{statement_id}/ack"`
- `post` `/statements/{statement_id}/mark-paid"`
- `get` `/statements/{statement_id}/download"`
- `get` `/orders/{order_id}/shipments"`
- `get` `/orders/{order_id}/after-sales"`

## h5/dingtalk.py  （2 端点）

- `- `get"`/dingtalk/bind-url"`
- `- `get"`/dingtalk/bind-status"`
- `get` `/dingtalk/bind-url"`

## h5/feishu.py  （2 端点）

- `- `get"`/feishu/bind-url"`
- `- `get"`/feishu/bind-status"`
- `get` `/feishu/bind-url"`

## h5/notifications.py  （4 端点）

- `- `get"`"`
- `- `post"`/read"`
- `- `post"`/read-all"`
- `- `get"`/unread-count"`
- `get` `"`
- `post` `/read"`
- `post` `/read-all"`

## h5/public_trace.py  （2 端点）

- `- `get"`/trace/{code}"`
- `- `get"`/trace/media/{attachment_id}"`
- `get` `/trace/{code}"`

## h5/report_units.py  （4 端点）

- `- `get"`/tasks/{task_code}/units"`
- `- `post"`/report-units"`
- `- `get"`/report-units"`
- `- `get"`/report-units/{unit_id}"`
- `get` `/tasks/{task_code}/units"`
- `post` `/report-units"`
- `get` `/report-units"`

## h5/salary_slips.py  （3 端点）

- `- `get"`/slip"`
- `- `post"`/slip/sign"`
- `- `post"`/slip/reject"`
- `get` `/slip"`
- `post` `/slip/sign"`

## h5/settings_media.py  （2 端点）

- `- `get"`/settings/report-media"`
- `- `get"`/settings/report-mode"`
- `get` `/settings/report-media"`

## h5/tasks.py  （9 端点）

- `- `get"`/tasks"`
- `- `get"`/reports/my-work-orders"`
- `- `get"`/tasks/{task_code}"`
- `- `get"`/tasks/{task_code}/qr"`
- `- `post"`/reports"`
- `- `get"`/reports"`
- `- `get"`/salary"`
- `- `get"`/salary/summary"`
- `- `get"`/dashboard/summary"`
- `get` `/tasks"`
- `get` `/reports/my-work-orders"`
- `get` `/tasks/{task_code}"`
- `get` `/tasks/{task_code}/qr"`
- `post` `/reports"`
- `get` `/reports"`
- `get` `/salary"`
- `get` `/salary/summary"`

## h5/temp_reports.py  （3 端点）

- `- `get"`/temp-reports/options"`
- `- `post"`/temp-reports"`
- `- `get"`/temp-reports"`
- `get` `/temp-reports/options"`
- `post` `/temp-reports"`

## h5/wecom.py  （2 端点）

- `- `get"`/wecom/bind-url"`
- `- `get"`/wecom/bind-status"`
- `get` `/wecom/bind-url"`

## miniapp/auth.py  （2 端点）

- `- `post"`/login"`
- `- `post"`/bind-openid"`
- `post` `/login"`

## miniapp/subscribe.py  （3 端点）

- `- `get"`/wechat-mp/templates"`
- `- `post"`/wechat-mp/subscribe-record"`
- `- `get"`/wechat-mp/my-subscriptions"`
- `get` `/wechat-mp/templates"`
- `post` `/wechat-mp/subscribe-record"`

## payment/xunhu.py  （3 端点）

- `- `post"`/create"`
- `- `post"`/notify"`
- `- `get"`/return"`
- `post` `/create"`
- `post` `/notify"`

## platform/ai.py  （15 端点）

- `- `get"`/settings"`
- `- `put"`/settings"`
- `- `get"`/gateways"`
- `- `post"`/gateways"`
- `- `put"`/gateways/{gateway_id}"`
- `- `post"`/gateways/{gateway_id}/set-default"`
- `- `delete"`/gateways/{gateway_id}"`
- `- `get"`/models"`
- `- `post"`/models"`
- `- `put"`/models/{model_id}"`
- `- `post"`/models/{model_id}/set-default"`
- `- `delete"`/models/{model_id}"`
- `- `post"`/test"`
- `- `get"`/profile"`
- `- `put"`/profile"`
- `get` `/settings"`
- `put` `/settings"`
- `get` `/gateways"`
- `post` `/gateways"`
- `put` `/gateways/{gateway_id}"`
- `post` `/gateways/{gateway_id}/set-default"`
- `delete` `/gateways/{gateway_id}"`
- `get` `/models"`
- `post` `/models"`
- `put` `/models/{model_id}"`
- `post` `/models/{model_id}/set-default"`
- `delete` `/models/{model_id}"`
- `post` `/test"`
- `get` `/profile"`

## platform/auth.py  （4 端点）

- `- `post"`/login"`
- `- `get"`/me"`
- `- `put"`/profile"`
- `- `put"`/password"`
- `post` `/login"`
- `get` `/me"`
- `put` `/profile"`

## platform/packages.py  （4 端点）

- `- `get"`"`
- `- `post"`"`
- `- `put"`/{package_id}"`
- `- `delete"`/{package_id}"`
- `get` `"`
- `post` `"`
- `put` `/{package_id}"`

## platform/public.py  （3 端点）

- `- `get"`/public-config"`
- `- `get"`/public-packages"`
- `- `get"`/tenants/public/{tenant_code}"`
- `get` `/public-config"`
- `get` `/public-packages"`

## platform/settings.py  （2 端点）

- `- `get"`"`
- `- `put"`"`
- `get` `"`

## platform/storage.py  （3 端点）

- `- `get"`"`
- `- `put"`"`
- `- `post"`/test"`
- `get` `"`
- `put` `"`

## platform/subscription_orders.py  （2 端点）

- `- `get"`"`
- `- `post"`/{order_id}/mark-paid"`
- `get` `"`

## platform/tenants.py  （3 端点）

- `- `get"`"`
- `- `post"`"`
- `- `put"`/{tenant_id}"`
- `get` `"`
- `post` `"`

## v1/auth.py  （5 端点）

- `- `post"`/login"`
- `- `post"`/register-by-invite"`
- `- `get"`/me"`
- `- `put"`/profile"`
- `- `put"`/password"`
- `post` `/login"`
- `post` `/register-by-invite"`
- `get` `/me"`
- `put` `/profile"`

## v1/captcha.py  （1 端点）

- `- `get"`"`

## v1/files.py  （3 端点）

- `- `post"`/upload"`
- `- `get"`/{attachment_id}/public"`
- `- `get"`/{attachment_id}"`
- `post` `/upload"`
- `get` `/{attachment_id}/public"`

## v1/push_monitor.py  （4 端点）

- `- `get"`/status"`
- `- `get"`/logs/{channel}"`
- `- `post"`/test/{channel}"`
- `- `post"`/clear-queue"`
- `get` `/status"`
- `get` `/logs/{channel}"`
- `post` `/test/{channel}"`

## v1/tenants.py  （1 端点）

- `- `post"`/register"`

## wecom/router.py  （3 端点）

- `- `get"`/callback"`
- `- `post"`/callback"`
- `- `get"`/oauth/callback"`
- `get` `/callback"`
- `post` `/callback"`

---
共 809 端点。
