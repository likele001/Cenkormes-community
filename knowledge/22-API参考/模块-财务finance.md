# 财务 · finance

> 实现：`api/admin/finance/router.py`；表 `statements`、`finance_ledgers`。
> 应收应付、往来账、利润与应付分析。

## 对账/往来（/admin/finance）
| 功能 | 方法/路径 | 说明 |
|------|----------|------|
| 列表 | GET `` | customer_id / status / offset / limit |
| 明细 | — | period_start/end、total_amount、amount、biz_date |
| 确认 | POST `/statements/{id}/confirm` | — |
| 收款 | POST `/{statement_id}/mark-paid` | 联动 _refresh_receivable_status/_refresh_payable_status，同步订单 paid_amount+payment_status |
| 打印 | GET `/statements/{id}/print` / `print-pdf` | template_code=supplier_statement? |

## 往来账（/admin/finance/ledgers）
GET：`direction / category / party_type / party_id / biz_date_from / biz_date_to / offset / limit`；POST 新增一笔。

## 利润（/admin/finance/profit）
- `month`（必填，`^\d{4}-\d{2}$`）：返回 `revenue / cost / gross_profit`，及客户/供应商维度汇总。

## 应付（/admin/finance/payables）
按 party 聚合：`total_payable / paid_amount / unpaid_amount`。

## 关键联动（记忆沉淀）
- 创建销售/采购发票时自动生成应收/应付（_gen_receivable/_gen_payable）
- 发票建在销售订单之上时，`total_amount` 取「订单总额 − 已收」，并强制用订单的 customer_id/supplier_id
- 金额字段 Decimal，求和/比较前 `float()` 或 `Decimal` 统一起点
