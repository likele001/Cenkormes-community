# 工资条 · salary_slip

> 实现：`api/h5/salary_slips.py`；表 `salary_slips`；前端路径 `/salary/slips`（H5 员工端）。

## 查看（GET）
参数 `month`(≤7，形如 2026-09)；返回顶部字段脱敏后的工资条。
返回项字段：
- `item_amount`（应发） / `bonus_amount`（奖金） / `deduction_amount`（扣除） / `net_amount`（实发）

## 确认 / 修改
- 附件确认：`attachment_id`(≥1)、`reason`(≤255)
- 传参带 `month` 定位月份

## ★脱敏要求（重要）
- **工资条接口必须调 `mask_rows` 列脱敏**，phone/net_amount 等敏感字段后端统一掩码
- 小程序/前端仅展示后端返回，不做二次脱敏（改规则不用重发版）
- 接口路径为 `/salary/slips`，避免与 `/salary-slips` 动态路由冲突

## 联动
- 报工质量/数量 → 工资项（salary_items、salary_allowances）
- 确认后参与月度核算
