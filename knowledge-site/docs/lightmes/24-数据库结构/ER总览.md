# ER 总览（核心域关系）

> 高度简化的核心实体关系，便于理解主流程。表名见 [表清单.md](表清单.md)。

```
               平台层 / 多租户
  tenants(租户) ──< users(用户) ──< roles(角色) ──<-> permissions(权限)
      │                 │
      │                 ├── salary_slips(工资条)   employee_skills
      │                 └── report_units(报工)
      │
  主数据（租户内）
   customers(客户) ──< customer_products(客户产品)
   products(产品) ───< skus(SKU) ──< bom(物料清单 BOM) ───<[ material / supplier ]
   processes(工序) ──< process_routes(工艺路线)   process_prices(工序单价)
   equipment(设备) ──< equipment_check/maintenance   molds(模具)
   suppliers(供应商) ──< materials(物料)   suppliers_statements(对账单)

  销售/订单
   orders(销售订单) ──< order_items ──> skus       customers(客户)
   quotations(报价) ──< quotation_items
   shipments(发货) ──< shipment_items ──> orders

  生产
   production_plans(计划) ──> tasks(任务) ──< task_assignments(派工)
   work_orders(工单) ──< report_units(报工) ──< work_order_pieces(件数)
   mrp_runs(MRP运算)  plan_purchase_links(计划采购关联)

  采购
   purchase_orders(采购单) ──> suppliers    incoming_batches(来料批次)

  库存
   warehouses(仓库) ──< stock(库存) ──< stock_logs(流水)   warehouse_entries(出入库)   material_issues(领料)

  质量
   inspection_templates(检验模板) ──< inspection_records(检验记录)   defect_codes(缺陷)
   spc_charts(SPC)

  财务/ERP
   statements(对账单) ──< statement_items(账期)   finance_ledgers(往来账)
   erp: account_subjects(科目) / vouchers(凭证) / invoices(发票) / fixed_assets(资产) / work_order_costs(成本)

  审批/工作流    workflow: approval_flows(流程) ──< approval_instances(实例)  ←订单/采购可配置启用
  消息推送       feishu_push_logs / wecom_push_logs / dingtalk_push_logs / wechat_mp_push_logs

  权限/ABAC     data_scopes(ABAC策略)  roles/permissions
```
