# 采购 · purchase

> 实现：`api/admin/purchase/orders.py`、`api/admin/purchase/statements.py`；表 `purchase_orders`、`supplier_statements`。
> 采购单 + 供应商对账，含收货/退货/取消、批量导出与打印。

## 采购单（/admin/purchase/orders）
| 功能 | 方法/路径 | 说明 |
|------|----------|------|
| 列表 | GET `/orders` | keyword / supplier_id / status / offset / limit(≤200) |
| 新增 | POST `/orders` | — |
| 详情 | GET `/orders/{order_id}` | — |
| 确认 | POST `/orders/{order_id}/confirm` | 确认后写 confirmed_at |
| 收货 | POST `/orders/{order_id}/receive` | 收货**扣库存入库**并写库存流水 |
| 退货 | POST `/orders/{order_id}/return` | — |
| 批号 | GET `/orders/{order_id}/batches` | 来料批次 |
| 取消 | POST `/orders/{order_id}/cancel` | — |
| 打印 | GET `/orders/{order_id}/print` / `print-pdf` | template_code=purchase_order |

核心字段：`unit_price`(Decimal→float 输出)、`confirmed_at`、`created_at`。

## 供应商对账（/admin/purchase/statements）
- 列表 GET ``：keyword/supplier_id/status/offset/limit；`amount`
- 新增 POST ``；导出 POST `/export` + 查任务 GET `/export-jobs`
- 明细字段：`period_from/period_to/confirmed_at/paid_at/created_at`
- 打印：`template_code=supplier_statement`；PDF：`/statements/{id}/print-pdf`

## 二次开发注意
- 金额用 Numeric/Decimal，输出统一 `float(...)`，避免求和 `TypeError`
- 收货/退货的逻辑涉及库存增减，注意与库存流水事务保持一致
