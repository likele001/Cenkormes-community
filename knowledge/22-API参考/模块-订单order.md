# 订单 · order

> 实现：`api/admin/production/orders.py`；schema：`schemas/order.py`；表 `orders`、`order_items`。
> 销售订单，含明细管理、审批流（条件启用）、ERP 导入、打印。

## 创建（OrderCreateIn）
| 字段 | 类型 | 说明 |
|------|------|------|
| customer_id | int ≥1 | 客户 |
| code | string ≤64 | 单号（缺省自动生成） |
| due_date | date | 交期 |
| remark | string | 备注 |
| opportunity_id | int | 关联商机(CRM) |

明细：`OrderItemCreateIn` = line_no / sku_id / qty / remark。
编辑明细用 `OrderItemUpsertIn`（带 id 则更新，否则新增）。

## 更新（OrderUpdateIn）
customer_id / code / due_date / remark 均可选改。

## 查询
keyword(搜索)、customer_id、opportunity_id、status、offset/limit(≤200)。

## 门户下单（portal CustomerPlaceOrderIn）
due_date / remark / submit(true=直接提交)。

## 审批流（条件启用，tenant 配置）
- **启用** → 提交订单创建 `pending_confirm` 审批实例，走工作流
- **禁用** → 提交直接确认，绕过工作流
- 审批中心前端走 `/admin/workflow` 前缀
- 订单打印：`template_code=order_detail` 默认模板

## ERP 联动
- ERP 导入走 Form：`customer_id/order_name/order_code/auto_create_product/auto_create_sku/default_unit_price` 等（`_form_unit_price` 转 Decimal）
