# 库存 · warehouse

> 实现：`api/admin/warehouse/router.py`、`material_issues.py`；表 `warehouses`、`stock`、`stock_logs`、`material_issues`。
> 仓库管理、库存增减（带锁防并发）、出入库流水、领料/退料。

## 仓库（/admin/warehouse/warehouses）
- 新增 `WarehouseCreateIn`：`code`(≤32,唯一性 `_warehouse_code_exists`)、`name`(1–128 必填)、`address`(≤255)
- 列表/导出/新增/编辑 PUT `/warehouses/{id}`

## 库存（/admin/warehouse/stocks）
| 功能 | 路径 | 说明 |
|------|------|------|
| 查询 | GET `/stocks` | warehouse_id / item_type |
| 调整 | POST `/stocks/adjust` | change_qty（**正=入库 负=出库**）、biz_type(默认manual)、remark；**`with_for_update()` 锁行防并发** |
| 流水 | GET `/logs` | warehouse_id / sku_id / item_type / offset/limit |
| 导出 | POST `/stocks/export` | + `/export-jobs` 查任务 |

## 领料/退料（/admin/warehouse/material_issues）
- 领料 `IssueCreateIn`：`warehouse_id`(≥1) / `work_order_id` / `remark`；明细 `IssueItemIn` = material_id / sku_id / qty(≥1)
- 退料 `ReturnCreateIn` + `ReturnItemIn`（带 `issue_item_id` 关联）
- 列表查询：warehouse_id / work_order_id / status
- 成本：`unit_cost / cost_amount / total_cost`

## 二次开发注意
- 出入库是**负向扣减/正向增加**，同一 `_apply_stock` 内 `with_for_update()` 锁行
- 每次变动写 `stock_logs` 流水，保证可追溯
