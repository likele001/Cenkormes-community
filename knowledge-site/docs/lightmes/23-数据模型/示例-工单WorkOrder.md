# 示例 · 工单 WorkOrder（表 work_orders）

> 本文为「如何写模型详细文档」的样例，字段来自 `backend/app/models/work_order.py` 真实定义。
> 其余模型见 [README-数据模型总索引](README-数据模型总索引.md)，逐个补齐即可。

## 元信息
- 所属域：生产
- 表：`work_orders`
- 软删除：否（无 deleted_at）
- 迁移：`0001_init.py` 起步，生产域在多期迁移中逐步扩展

## 用途
销售订单生成工单，作为生产执行与报工的载体，绑定订单明细、产品、SKU，记录工时与实际进度。

## 关键字段（models/work_order.py）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Int PK autoinc | 主键 |
| tenant_id | Int FK→tenants.id, CASCADE, index | 租户（隔离键） |
| order_id | Int FK→orders.id, CASCADE, index | 销售订单 |
| order_item_id | Int FK→order_items.id, CASCADE, index | 订单明细 |
| product_id | Int FK→products.id, RESTRICT, index | 产品 |
| sku_id | Int FK→skus.id, RESTRICT, index | SKU |
| qty | Int | 数量 |
| status | Str(32), default 'open', index | 状态（open/…） |
| standard_hours | Numeric(10,2), default 0 | 标准工时 |
| actual_hours | Numeric(10,2), default 0 | 实际工时 |
| started_at / finished_at | DateTime nullable | 开始/完成时间 |
| created_at / updated_at | DateTime server_default now() | 审计时间 |

## 关系
- 所属：`orders`、`order_items`、`products`、`skus`、`tenants`
- 被引用：`report_units`（报工）、`work_order_pieces`（件数）、`work_order_costs`（成本）

## 二次开发注意
- **序列化嵌套**（关联 products/skus 等）查询需 `.options(selectinload(...))` 预加载，否则 `MissingGreenlet`
- **Numeric 字段**（standard_hours）是 Decimal，累加需 `float()` 转换
- 状态/工时的写操作端点务必 `await db.commit()`
