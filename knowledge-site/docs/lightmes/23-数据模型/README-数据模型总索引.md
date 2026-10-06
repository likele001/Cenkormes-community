# 数据模型总索引（81 模型）

> 按领域分类。定位：backend/app/models/*.py（SQLAlchemy，统一从 app.models 导出）。

## 主数据

- `code_sequence` → 表 `code_sequences`
- `customer` → 表 `customers`
- `customer_product` → 表 `customer_products`
- `department` → 表 `departments`
- `dictionary` → 表 `sys_dict_types`
- `equipment` → 表 `equipment`
- `material` → 表 `suppliers`
- `material_issue` → 表 `material_issues`
- `mold` → 表 `molds`
- `print_template` → 表 `print_templates`
- `process_price` → 表 `process_prices`
- `process_route` → 表 `process_routes`
- `process_skill` → 表 `process_skill_links`
- `product` → 表 `products`
- `production_calendar` → 表 `production_calendar_days`
- `production_plan` → 表 `production_plans`
- `shift` → 表 `shifts`
- `sku` → 表 `skus`
- `supplier` 
- `supplier_statement` → 表 `supplier_statements`
- `warehouse` → 表 `warehouses`
- `warehouse_entry` → 表 `warehouse_entries`

## 生产

- `automation_log` → 表 `automation_logs`
- `incoming_batch` → 表 `incoming_batches`
- `plan_purchase_link` → 表 `plan_purchase_links`
- `report` → 表 `reports`
- `report_unit` → 表 `report_units`
- `task` → 表 `tasks`
- `task_assignment` → 表 `task_assignments`
- `temp_report` → 表 `temp_reports`
- `work_order` → 表 `work_orders`
- `work_order_piece` → 表 `work_order_pieces`

## ERP

- `erp_asset` → 表 `fixed_assets`
- `erp_cost` → 表 `work_order_costs`
- `erp_invoice` → 表 `invoices`
- `erp_ledger` → 表 `account_subjects`
- `finance` → 表 `statements`
- `finance_ledger` → 表 `finance_ledgers`
- `purchase` → 表 `purchase_orders`
- `quotation` → 表 `quotations`
- `shipment` → 表 `shipment_items`

## 质量·薪酬

- `attendance` → 表 `attendance_records`
- `employee_skill` → 表 `skills`
- `quality` → 表 `inspection_templates`
- `salary` → 表 `salary_items`
- `salary_allowance` → 表 `salary_allowances`
- `salary_slip` → 表 `salary_slips`
- `spc` → 表 `spc_charts`

## 平台·SaaS

- `cron_job` → 表 `cron_jobs`
- `dingtalk_push_log` → 表 `dingtalk_push_logs`
- `export_job` → 表 `export_jobs`
- `feishu_push_log` → 表 `feishu_push_logs`
- `notification` → 表 `notifications`
- `operation_log` → 表 `operation_logs`
- `permission` → 表 `permissions`
- `platform_setting` → 表 `platform_settings`
- `platform_user` → 表 `platform_users`
- `role` → 表 `roles`
- `saas_package` → 表 `saas_packages`
- `subscription_order` → 表 `tenant_subscriptions`
- `system_version` → 表 `system_versions`
- `tenant` → 表 `tenants`
- `tenant_invite` → 表 `tenant_invites`
- `tenant_setting` → 表 `tenant_settings`
- `user` → 表 `users`
- `user_wechat_subscription` → 表 `user_wechat_subscriptions`
- `wechat_mp_push_log` → 表 `wechat_mp_push_logs`
- `wecom_push_log` → 表 `wecom_push_logs`

## 支撑·AI·审批

- `abac` → 表 `data_scopes`
- `ai` → 表 `platform_ai_profiles`
- `ai_employee` → 表 `ai_employees`
- `approval` → 表 `approval_flows`
- `attachment` → 表 `attachments`
- `trace` → 表 `trace_codes`
- `workflow` → 表 `approval_instances`

## 其它

- `crm` → 表 `customer_contacts`
- `mrp` → 表 `mrp_runs`
- `order` → 表 `orders`
- `process` → 表 `processes`
- `subcontract` → 表 `subcontract_orders`

---
模型文件：`backend/app/models/*.py`。表名以各模型 `__tablename__` 为准，迁移链见 24-数据库结构。
