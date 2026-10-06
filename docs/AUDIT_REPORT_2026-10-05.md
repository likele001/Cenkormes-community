# LightMes SaaS 审计报告

日期：2026-10-05 ｜ 范围：`/www/wwwroot/lightmes`（管理端 + H5 + 小程序 + FastAPI）
对照基准：`/www/wwwroot/cenkormes/docs/AUDIT_REPORT_2026-10.md`（独立版审计报告）
口径：一条业务数据从产生到能被对账、被追溯、被结算，这条路断在哪；SaaS 额外核对**多租户隔离**。

> 本文件分两部分：
> 1. **与 cenkormes 报告的对照结论**（已记录，2026-10-05）
> 2. **LightMes 全量审计结果**（已完成，2026-10-05）

---

## 整改进度：P0 / P1 / P2 / P3 全部完成（2026-10-06）

### P0（6/6 完成）

6 项 P0 问题已完成修复并通过回归验证，新增 6 个测试文件（37 个用例全通过）：

| # | 问题 | 修复方案 | 回归测试 |
| --- | --- | --- | --- |
| P0-1 | 工作流审批放行 + 转交无校验 | `check_available_approver` 按真实角色集合校验；`transfer_task` 校验操作人为当前审批人、目标用户为本租户启用用户 | `tests/test_workflow_approval.py`（6） |
| P0-2 | 外协发料跨租户 + 超发 | schema 强类型（qty ge=1）；`create_send_logs` 加 tenant/order 归属校验与「累计发料 ≤ 委外数量」护栏 | `tests/test_subcontract_send.py`（5） |
| P0-3 | 库存三接口缺归属校验 | 手工调整/入库单/领料退料补租户归属校验；`adjust_stock` 加非负护栏；`stocks.qty` 加 DB CHECK（migration 0075） | `tests/test_stock_guard.py`（6） |
| P0-4 | 双重入库 | `remark` 关键字锚定件次日志（与工单 id 域重叠问题解耦），工单级入库改「差额入库」：`pending = 良品总数 - 已按件入库数` | `tests/test_double_stockin.py`（6） |
| P0-5 | 越权改钱 | `/reports/salary/*` 拆出 `salary_router`：读挂 `salary.view/manage`（任一），写挂 `salary.manage` + 员工归属校验 | `tests/test_salary_permissions.py`（6） |
| P0-6 | 对账重复计费 | 销售侧订单级去重拒绝（`find_stated_order_ids`）；供应商侧流水级冲突检测（`_find_duplicate_stockins`，支持跨期增量对账不误伤） | `tests/test_statement_dedup.py`（8） |

验证结果（2026-10-06 终版）：全量 `pytest` **312 passed / 0 failed（全绿）**；`date_format` SQLite 兼容问题与 `test_boss_qa_mock` mock 目标问题均已在 P3-28 修复消除（312 = 307 + P4-31 新增发货取消 5）。前端 `vue-tsc`（admin）类型检查通过。

### P1（10/10 完成）

| # | 问题 | 修复方案 | 回归测试 |
| --- | --- | --- | --- |
| P1-7 | H5 客户自助 `mark-paid` 越权改账 | 改为「提交回款登记」（`payment_submitted_at/remark`），仅通知财务核实；正式入账仍由管理端 mark-paid 完成（migration `0076_stmt_payment_submit`） | `tests/test_statement_payment_submit.py`（6） |
| P1-8 | 发货/外协账实不符 | `shipments` / 外协发料·收回日志补 `warehouse_id`；发货支持指定仓（未指定回退默认仓并回写）；外协发料/收货可选仓库同步扣/加库存与 `subcontract_out/in` 流水（migration `0077_add_warehouse_refs`） | `tests/test_warehouse_accountability.py`（8） |
| P1-9 | 工资未进总账（人工成本缺位） | `salary_slips` 补 `pay_status/paid_at/paid_by/pay_method`；新增 `POST /salary/slips/{id}/pay` 发放端点（幂等+自愈补记，`net<=0` 不记账）→ 写 `FinanceLedger(out/labor, statement_type=salary_slip)`；`profit_api` 成本改为「采购+人工」并新增 `purchase_cost/labor_cost` 拆分；发放通知注册 `salary.slip_paid` 全渠道事件（migration `0078_salary_slip_pay`） | `tests/test_salary_ledger.py`（7） |
| P1-10 | 对账无逐笔核销 | 新表 `statement_payments`（customer/supplier 通用）：逐笔收款/付款核销端点（超额 400，每次核销写一条流水）；`mark-paid` 改差额核销（幂等+自愈补历史缺登记）；`statements`/`supplier_statements` 补 `due_date`；账龄计算（基准 = due_date → period_end/period_to → created_at，分桶 0-30/31-60/61-90/90+），列表/详情输出已核销/未核销/账龄（migration `0079_statement_payments`） | `tests/test_statement_payments.py`（11） |
| P1-11 | 签收快照被重算覆盖 | `ensure_salary_slip` 增加快照锁定：已签收（`signed_at` / `confirm_status=signed`）或已发放（`paid_at`）后不再重算覆盖金额；管理员重置签收可解除签收锁定，发放锁定不因重置解除（保护 `FinanceLedger` 金额一致） | `tests/test_salary_slip_lock.py`（6） |
| P1-12 | 临时报工绑定可绕过派工/计划额度、无留痕 | 绑定端点补双上限校验：员工有派工记录时绑定后累计不得超派工数；任务累计终审合格 + 本次绑定不得超任务计划数（未派工绑定的兜底护栏）；绑定成功写 `ReportAudit`（audit_level=qc / action=approve，reason 记录来源临时报工 id 与数量）；抽公共 `sum_task_done_good_qty` 与 `sync_task_progress` 完成口径统一 | `tests/test_temp_report_bind.py`（6） |
| P1-13 | 审核无职责分离（自审/一人两级） | 新增 `assert_report_audit_sod` / `assert_unit_audit_sod` 公共校验：所有审核动作（通过/驳回）拦截自审；终审/多级审核拦截与已审核人同人；覆盖 4 条通道——admin 报工/件次端点、IM 卡片（飞书/钉钉）、企微卡片；临时报工绑定（视为终审）补自审拦截 | `tests/test_audit_sod.py`（10） |
| P1-14 | 外协结算不动账 | `settle` 按 `Σ(unit_price × received_qty)` 写 `FinanceLedger`（out/subcontract，party=供应商，statement_type=subcontract_order，biz_date=结算日）；幂等（`ledger_exists_for_biz` 防状态回退重结算）；零金额不记账；`profit_api` 成本口径并入外协（返回 `subcontract_cost`），前端成本卡片展示外协成本 | `tests/test_subcontract_settle.py`（6） |
| P1-15 | 留痕覆盖不全 | 4 处敏感操作补 `operation_logs`（复用 `write_op_log`，含操作人/租户/对象/明细/路径）：工资条重置（salary/reset_confirm）、手工记账（finance/create_ledger，明细含方向/类别/金额/往来单位）、手工调库存（warehouse/adjust_stock，既有实现，本次补回归保护）、订单驳回（order/reject，保留 remark 追加行为，另加结构化留痕） | `tests/test_op_logs.py`（6） |
| P1-16 | 退料超领护栏 | `confirm_return` 补强：关联领料明细时校验（1）所属领料单必须已实际领料（issued）——draft/cancelled 未扣过库存，退料会凭空增库存；（2）累计退料（status=returned 口径）不得超过已领量。基础护栏（单次/累计超领、跨单明细）已在 `test_stock_guard.py`，本次补「未领可退」缺口并锁定边界口径 | `tests/test_material_return_guard.py`（5） |

### P2（9/9 完成）

| # | 问题 | 修复方案 | 回归测试 |
| --- | --- | --- | --- |
| P2-17 | 飞书事件回调无验签（可伪造第三方回调） | 新增 `verify_event_token`：租户配置了 `verification_token` 时强制校验回调 token（`header.token` / 顶层 `token`，兼容 AES 加密回调体），不匹配 403；未配置时放行（兼容旧部署） | `tests/test_feishu_verify.py`（8） |
| P2-18 | 导出任务越权读（同租户普通用户可读薪资导出） | `job_type` → 权限码映射（salary_excel→`salary.manage`、finance_statement→`finance.manage` 等）+ owner-or-permission 校验；未知类型 fail-closed 403 | `tests/test_export_job_access.py`（6） |
| P2-19 | 通知未注册事件静默丢弃（配置成功实际不发） | `dispatch` 结尾对未分类事件记 warning（含 `event_code/tenant_id/title`），不抛异常以免打断业务事务 | `tests/test_notify_unregistered.py`（16） |
| P2-20 | MRP 细节偏差（停用仓计入可用 / convert 仅单供应商） | 库存汇总 join `Warehouse` 过滤 `is_active`（MRP/齐套/领料可用量口径统一）；`convert` 的 `supplier_id` 改可选：留空按物料默认供应商自动分单（`orders` 多单返回），指定时保留合并行为 + 顶层 `code` 兼容；顺带修复前端 `run/convert` 用 query 传参而后端读 body 的错位 | `tests/test_mrp_convert_split.py`（7） |
| P2-23 | 采购作废无 reason、`partial_received` 可直接一键作废 | `cancel` 接受可选 `{reason}`；`partial_received` 作废 reason 必填（400，防掩盖已收货事实），原因写入 `operation_logs.detail`；前端该状态改弹窗输入原因 | `tests/test_purchase_cancel.py`（5） |
| P2-24 | 金额口径分裂（订单确认缺价容错记 0 vs 对账直接 raise） | `crud/finance.scan_order_statement` 统一扫描：返回（金额, 问题列表）不抛异常（no_items/sku_missing/no_route/missing_price）；`POST /finance` 全量收集后一次性 400（附「先维护型号工价」指引，替代逐单首个 raise）；新增 `GET /statements/precheck` 预检端点（逐单 ok/reason/issues，不写库不阻断） | `tests/test_statement_precheck.py`（10） |
| P2-22 | `cron_jobs` 部署级配置挂在租户权限下（任一租户管理员可改整个部署调度） | 双模式收敛：新增平台端 `/api/platform/cron-jobs`（list/update/reload/defaults，挂平台超管）；SaaS 模式（`saas_mode_enabled`）下 admin 写操作 403 并指引平台后台，GET 只读可用；私有化模式保持可写；逻辑抽到 `crud/cron_job` 共用；前端新增平台后台页面 + 租户页 SaaS 只读提示；顺带修复 en-US 语言包 cronJobs 段整段缺失 | `tests/test_cron_jobs_mode.py`（11） |
| P2-25 | `leader-approve` 无行锁（并发重复审计流水） | `get_report_by_id(for_update=True)`，与 `qc-approve` 行锁口径一致 | 既有审核套件覆盖 |
| P2-21 | 库存盘点功能缺失（仓库/库存无盘点单） | 新增盘点闭环：`stock_checks` / `stock_check_items` 两表 + `/admin/warehouse/stock-checks` 6 端点——建单（全盘快照该仓全部库存行 / 抽盘指定型号、无库存按账面 0 支持盘盈）→ 录入实盘 → 完成时逐行 `adjust_stock(diff)` 并写 `stock_check` 流水（diff=0 不写），完成后锁定；前端盘点页面（新建/详情录入/完成）+ 路由菜单 + i18n；顺带补齐 `BizType.STOCK_CHECK` 编号规则（migration `0080_stock_checks`） | `tests/test_stock_check.py`（20） |

✅ 迁移已执行：`0075` → `0076` → `0077` → `0078` → `0079` → `0080`（DB 当前 head = `0080_stock_checks`；`statement_payments` 表 + 两表 `due_date` 列、`salary_slips` 四列、`stock_checks` / `stock_check_items` 两表均已落库；存量 9 行 `pay_status` 回填 `unpaid`）。

> ⚠️ 经验：`alembic_version.version_num` 为 VARCHAR(32)，**revision id 不得超过 32 字符**（0076 原 id 33 字符导致版本写入失败，DDL 幂等可安全重跑；已缩短为 `0076_stmt_payment_submit`）。

---

## 第一部分：与 cenkormes 报告的对照结论

### 1.1 SaaS 同样存在的问题（确认）

| # | 问题 | 关键证据 | 对应 cenkormes 条目 |
| --- | --- | --- | --- |
| 1 | **越权改钱**：`POST /admin/production/reports/salary/allowances`（新增/修改工资补贴）挂在 `report.audit` 权限下，qc 角色预设含 `report.audit` → 质检员/班组长可给任意员工加工资补贴 | `backend/app/api/admin/production/reports.py:25`（router 依赖）、`:317`（POST）、`backend/app/core/seed.py:63`（qc 预设）；前端调用 `frontend-admin-pro/src/api/salary.ts:119/132`、`api/production.ts:1385/1398` | P1.1 |
| 2 | **发货不记仓库**：`shipments` 无 `warehouse_id`，发货时"取最低 ID 的启用仓"扣库存，单据上看不到扣了哪个仓 | `backend/app/models/shipment.py`（Shipment 无 warehouse_id）；`backend/app/api/admin/warehouse/shipments.py:117-120` | 0008 账实一致 |
| 3 | **外协发出/收回不进库存流水**：`subcontract_send_logs` / `subcontract_receive_logs` 无 `warehouse_id`，发料只累加 `sent_qty`，不碰库存 | `backend/app/models/subcontract.py`；`backend/app/crud/subcontract.py` | 0008 账实一致 |
| 4 | **工资未进总账**：`SalarySlip` 只有签收（`confirm_status`），无 `pay_status/paid_at/paid_by/pay_method`；无 `FinanceLedger(category=labor)` 写入 → 人工成本在现金流上缺位 | `backend/app/models/salary_slip.py`；`backend/app/crud/salary_slip.py`（仅 sign/reject/reset） | 0009 工资落账 |
| 5 | **对账无逐笔核销**：`mark-paid` 一次性全额置 paid + 一条幂等 ledger；无 `statement_payments`、无部分收款、无 due_date/账龄 | `backend/app/api/admin/finance/router.py:392-426`；供应商侧 `api/admin/purchase/statements.py:341` | 0007 应收口径 |
| 6 | **留痕覆盖不全**：订单/采购审批有 workflow `ApprovalRecord`（仅 order/purchase 两类）；**工资条撤销**直接清空 signed_at/reject_reason；**订单驳回**只把原因追加进 remark 文本；**应收核销**无日志 | `backend/app/services/workflow/biz_hooks.py`（仅 order/purchase）；`backend/app/crud/salary_slip.py:151`；`backend/app/crud/order.py:371` | 0010 审批留痕 |
| 7 | **MRP 细节偏差**：① 库存统计不过滤启用仓（停用仓库存也算可用）② `convert` 一次只能指定单一供应商，无按供应商分单 | `backend/app/crud/warehouse.py:116`（`sum_stock_qty_by_sku_ids` 无 is_active 过滤）；`backend/app/services/mrp_suggestion.py:11` | 0011 MRP 落地 |
| 8 | **通知未注册事件静默返回 0**：事件分类是硬编码 frozenset，不在其中即静默丢弃，页面显示配置成功、实际一条不发 | `backend/app/services/notify_dispatcher.py:468`；`backend/app/services/notify_channels.py:49-101` | P2.5 |
| 9 | **`stocks.qty` 无 DB CHECK 且 crud 不拦负**：`adjust_stock` 直接 `s.qty += change_qty`，负数全靠调用方自觉 | `backend/app/models/warehouse.py:25-41`（无 CheckConstraint）；`backend/app/crud/warehouse.py:66-81` | P2.6 |

### 1.2 SaaS 不存在的问题（与 cenkormes 不同）

| cenkormes 问题 | SaaS 状态 | 证据 |
| --- | --- | --- |
| P1.2 外协 router 无权限依赖 | **已挂** `subcontract.manage` | `backend/app/api/admin/subcontract/router.py:47` |
| P1.3 WS 只有连接没有推送 | **有生产者**：`broadcast_sync` 在 3 处调用（报工/报工单/临时报工） | `api/admin/production/reports.py:206`、`temp_reports.py:167`、`report_units.py:451` |
| P2.4 automation dry-run/logs 前端没接 | **已接**：`AutomationSettingsPage.vue` 同时用 logs + dry-run | `frontend-admin-pro/src/pages/system/AutomationSettingsPage.vue:343/363` |
| P3.8 ai/erp 权限码属下线模块 | SaaS 有完好 AI/ERP 模块，权限码有实际使用 | `api/admin/ai/*`、`api/admin/erp/*` |
| §4.1 Alembic 不是 schema 唯一真相 | **不存在**：`0001_init.py` 显式建表，无任何 migration 用 `create_all`，86 个 migration 链完整 | `backend/alembic/versions/0001_init.py` |
| §4.3 演示脚本传不存在的 tenant_id | **不适用**（SaaS 多租户，tenant_id 合法） | — |
| P3.7 空转权限码 20/57 | **已闭环**：4 个无引用码全部处理（`salary.view` P0-5 接线；`tenant.manage`/`report.submit`/`report.work_self` P3-30 删除） | 脚本比对 `backend/app/core/seed.py` 与 `app/` 引用；扫描双空（声明未使用 / 使用未声明） |

### 1.3 轻微项

- ✅ **[已处理]** `src/api/salary.ts` 与 `src/api/production.ts` 重复包装同一对 allowances 接口（P3-30 删 `salary.ts` 版本，`SalaryPage.vue` 用 `production.ts` 版本）；`src/` 下残留备份文件（P3-27 归档至 `.local-backups/archive_20261006/`）。
- ✅ **[已处理]** `backend/.env`：已改 `APP_ENV=prod`、`DB_AUTO_CREATE=false`、`DB_AUTO_SEED=false`（P3-26，重启后端后生效）。

### 1.4 建议处理顺序（对照部分）

1. 补贴接口拆权限（越权改钱，改动最小）
2. 发货记仓库 + 外协记库存流水（账实一致）
3. 工资发放落账（四列 + 发放动作 + `FinanceLedger(labor)`）
4. 留痕补口（工资条撤销 / 应收核销 / 补贴新增）
5. 通知未知事件改为报错或落失败记录；`stocks` 补 CHECK
6. MRP：库存过滤启用仓、convert 按供应商分单

---

## 第二部分：LightMes 全量审计结果

### 2.1 多租户隔离专项（已核对）

| 检查点 | 结论 |
| --- | --- |
| 附件服务 `api/admin/system/attachments.py` | 全部按 `tenant_id` 过滤（列表/详情/签名URL/删除）✓ |
| 文件服务 `api/v1/files.py` | 下载/上传均校验租户；公共读图 `/files/{id}/public` 需短期 HMAC 签名 + 显式 tenant ✓ |
| 导出任务 `api/admin/export_jobs.py` | 按 `tenant_id` 取任务 ✓ |
| WebSocket `api/ws/dashboard.py` | 校验 token 中 user_id/tenant_id 一致 + `is_active`，按租户分房间 ✓ |
| 平台端 `api/platform/*` | 除登录/公开页外全部挂 `get_current_platform_user` ✓ |
| 支付回调 `api/payment/xunhu.py` | `verify_notify` 验签后处理 ✓ |
| 后台任务 `app/tasks/*` | 按租户循环、逐租户查询（crm/salary/ai）✓ |
| API 层 `db.get()` 抽查（35 处） | 抽查 12 处高风险点均带 `tenant_id` 校验（ws/dingtalk/wecom/purchase 仓库/任务设备等）✓ |
| 公开溯源 `api/h5/public_trace.py` | 媒体出口有"仅该件号 QC 通过报工附件"白名单校验 ✓ |

**观察项（1 处，低风险）**：`api/admin/cron_jobs.py` 的定时任务为**部署级全局单例**（模型注释声明非租户隔离），但接口只挂租户级 `setting.manage` 权限 → **任一租户的管理员都能改动整个部署的 Celery Beat 调度**（关掉别人的日报推送等）。建议收敛到平台端或只读展示。

### 2.2 销售-发货-对账-收款闭环

| 检查点 | 结论 |
| --- | --- |
| 订单确认金额 | `_fill_order_amount` 容错：缺工价/单价时**记 0 不报错**（`crud/order.py:381-435`）；而对账侧 `calc_order_statement_amount` 缺工价直接 raise（`crud/finance.py:14-48`）→ 订单能确认、对账必失败，口径分裂 |
| 订单驳回 | 只把原因追加进 `remark` 文本，无结构化留痕（`crud/order.py:371-379`） |
| 发货 | ✅ **[已修复]** 超额发货护栏存在 ✓（累计发货 ≤ 订单量）；扣库存/单据仓库字段已补（P1-8）；取消端点已补（P4-31：`POST /shipments/{id}/cancel`，pending 直接取消、shipped 回滚库存 + `ship_cancel` 流水 + 订单状态回退，signed 不可取消） |
| 对账重复计费 | `POST /admin/finance/statements` 生成对账单**无去重**：同一订单可反复生成对账单重复入账；`Order`/`OrderStatementItem` 无「已对账」标记，全库无此检查（`api/admin/finance/router.py:300-372`；`crud/finance.py:51-78`） |
| 收款 | 管理端 `mark-paid` 全额置 paid + 幂等 ledger ✓（`ledger_exists_for_statement`，`finance/router.py:392-426`）；**无部分收款/逐笔核销/账龄**（0007 未落地） |
| H5 客户自助收款 | `api/h5/customer.py:465-505`：**客户可自行把对账单标记已付款**并写收入 ledger（无核实环节）→ 外部角色越权改账 |
| 利润 | `profit_api` 按现金口径 `收款-付款`，**无人工（labor）成本**（`finance/router.py:163-247`） |
| 手工记账 | 手工 ledger 分录无 op log（`finance/router.py:137-160`） |

### 2.3 采购-入库-对账-付款闭环

| 检查点 | 结论 |
| --- | --- |
| 收货/退货护栏 | **齐全** ✓：累计收货 ≤ 订购量、退货 < 已收（`purchase/orders.py:179-274` 收货、`:277-366` 退货） |
| 作废 | `cancel` 无 reason 参数；`partial_received` 状态也可直接作废（`purchase/orders.py:395-418`） |
| 对账重复计费 | `_calc_inbound_summary` 按期间从 `StockLog(biz_type=purchase_in)` 汇总，**与存量对账单无任何关联/排除**；`period_from/to` 均为可选，不填=全量 → 同一批入库可被多张对账单重复计费（`crud/supplier_statement.py:49-109`、`:112-151`） |
| 付款 | 状态机守卫 `confirmed → paid` 单向，重复调用报错，ledger 不会重复入账 ✓（`crud/supplier_statement.py:164-186`） |
| 入库单 | 手工入库单 create 无仓库/采购单/退料单归属校验（详见 2.4） |

### 2.4 库存闭环

| 检查点 | 结论 |
| --- | --- |
| **双重入库（高）** | 单位报工模式下，件次终审通过按件 `+1` 入库（`produce_in`，`biz_id=unit.id`，`production/report_units.py:415-430`）；工单全部任务完成时 `stock_in_work_order` **再按 `sum_work_order_good_qty` 全量入库一次**（`biz_id=wo.id`，由 `crud/task.py:161-176` 触发）。幂等检查 `work_order_already_stocked_in` 只认 `biz_id=wo.id`，查不到按件日志 → **同批良品入账两次、库存虚增**（`crud/work_order.py:87-131`） |
| 负库存无护栏 | `adjust_stock` 直接 `s.qty += change_qty`，无任何非负校验（`crud/warehouse.py:66-91`）；领料出库（`crud/material_issue.py:92-110`）、发货、手工调整全部可打出负库存；`stocks` 表无 CHECK（P2.6） |
| 手工调整库存 | `POST /admin/warehouse/stocks/adjust` **不校验仓库/SKU 租户归属**、无负数护栏、无 op log（`warehouse/router.py:138-151`；`crud/warehouse.py:35-41` `get_or_create_stock` 不校验 warehouse 归属） |
| 入库单 | `POST /entries` 不校验 `warehouse_id`/`purchase_order_id`/`material_return_id` 归属（`warehouse_entries.py:103-142`）→ 确认入库时可把库存记到「别人的仓 ID」名下 |
| 领料/退料 | create 不校验 warehouse/work_order/issue 归属，列表输出带他租户仓名/物料名（关系对象无租户过滤，`crud/material_issue.py:58-89`、`:160-193`；`_issue_out` `:59-77`）；`issue_materials` 无足量校验；`confirm_return` **无超领护栏**（`issue_item_id` 可选且不校验退料量 ≤ 已领量，`:196-214`）→ 库存虚增 |
| 盘点 | **仓库/库存无盘点功能**（仅 ERP 固定资产有盘点单，`api/admin/erp/assets.py:298+`）→ 账实差异无盘点单纠偏途径 |
| 默认仓口径 | 三处均「取 ID 最小的启用仓」靠猜：发货（`shipments.py:117-120`）、工单完工入库（`crud/work_order.py:77-84`）、件次入库（`report_units.py:420-424`） |
| 物料/成品判定 | 按 SKU 编码前缀 `MAT-` 猜物料/成品（`crud/warehouse.py:58-61`、`:108-111`）——轻 |
| 在途口径 | `sum_stock_qty_by_sku_ids` 不过滤停用仓（见 1.1#7） |

### 2.5 生产闭环

| 检查点 | 结论 |
| --- | --- |
| 计划→下发链 | **护栏完整** ✓：仅已审核订单可建计划、重复下发只同步不重复建单、齐套检查（`allow_shortage` 需显式勾选）、订单状态机单向、缺工艺路线直接 raise（`plans.py:1380-1453`、`crud/production_plan.py:202-269`、`crud/order.py:216-253/437-454`） |
| **审核 SoD 缺失** | `leader-approve`/`qc-approve` 及件次多步审核均无「审核人≠报工人」「初审人≠终审人」校验 → 持有 `report.audit` 的人可自报自审、一人走完两级审核（`reports.py:131-227`、`report_units.py:258-375`） |
| **临时报工绑定直通终审** | `temp_reports.py:117-128`：绑定即置 `qc_approved`，**不写 ReportAudit 留痕**、不调 `validate_report_qty_limit`（派工上限）→ 可超量并入并发薪 |
| 派工护栏 | ✓ 派工合计≤计划、不得小于已报、已有报工不可撤派（`crud/task_assignment.py:202-250`）；报工超派工上限拦截（`:335-353`）；未派工不可报（H5 走同一校验） |
| 工资数据权限 | `/reports/salary/*`（明细/汇总/补贴）整组挂 `report.audit`（`reports.py:25`）→ qc 角色可看全厂工资；`salary.view` 权限码存在但全库无引用 |
| 件次审核 | ✓ 终审必须上传质检附件；致命缺陷自动驳回并重置为 draft + 通知（`report_units.py:284-336`） |
| 报工计薪 | ✓ 缺工价时通知超管（不静默）、`SalaryItem` 按 report_id upsert 幂等（`crud/report.py:136-172`） |
| 并发细节 | `leader-approve` 无行锁（`qc-approve` 有 `for_update`）→ 并发下可能重复审计流水（轻，`reports.py:131-157` vs `:166`） |
| 代码卫生 | `plans.py` 的 `/plans/{id}/forecast`、`/aps-strategy` 各注册两次（`:1751-1788`），后者为死路由 |

### 2.6 工资 / 外协 / MRP / 质量 / 溯源

| 检查点 | 结论 |
| --- | --- |
| **工资条签收快照不锁定** | `ensure_salary_slip` 每次调用重算金额并回写（`crud/salary_slip.py:77-97`）；H5 查看即触发（`h5/salary_slips.py:27`）→ 已签收工资条的金额可被后续补贴/报工变动改写 |
| 工资发放未落账 | `SalarySlip` 无 `pay_status/paid_at/paid_by/pay_method`，无 `FinanceLedger(labor)`（Part 1 #4） |
| 重置无留痕 | `reset-confirm` 清空签收/拒签信息，仅发通知不写 op log（`crud/salary_slip.py:151-161`、`salary_reports.py:324-346`） |
| 补贴录入 | `create_allowance_api` 不校验 `payload.user_id` 归属（`reports.py:317-336`），可挂到不存在/他租户用户（低） |
| **外协发料跨租户写入 + 超发无拦（高）** | `SubcontractSendIn.sends` 是无类型 `list[dict]`（`schemas/subcontract.py:48-50`）；`create_send_logs` 按 item_id 直接 `sent_qty += qty`，**不校验 item 的 tenant_id/order_id 归属、无上限、qty 可为负**（`crud/subcontract.py:91-121`）→ 传他租户 item_id 可改别人数据；超发无护栏（对比收货有 `:367`） |
| 外协结算不动账 | `settle` 只改状态：`unit_price × received_qty` 不生成任何付款单/ledger（`subcontract/router.py:387-395`）→ 委外成本不进财务 |
| 外协归属校验 | create/add_items 不校验 supplier/sku/process 归属，输出带他租户名称（`subcontract/router.py:278-325`） |
| MRP | 净需求减在途 ✓（`crud/mrp.py:133`）；convert 仅单供应商、库存不过滤停用仓（Part 1 #7） |
| 质量 | ✓ 模板/缺陷码租户隔离；件次终审质检记录 + 致命缺陷联动驳回 |
| 溯源 | ✓ 公开查询白名单校验（Phase A）；码链在终审生成、工序事件链完整 |

### 2.7 权限安全全景

| 检查点 | 结论 |
| --- | --- |
| 全局门禁 | ✓ 全部 `/admin/*` 经 `_admin_deps=[Depends(require_admin_portal_user)]`（`api/router.py:43-115`）；H5/小程序/公开回调独立挂载 |
| 模块权限覆盖 | ✅ **[已处理]** 4 个未用权限码已闭环（`salary.view` P0-5 接线；`report.submit`/`report.work_self`/`tenant.manage` P3-30 删除，扫描双空）；ERP 子路由经父 router 继承 `erp.manage` ✓ |
| **工作流审批可被任意管理端用户放行（高）** | `check_available_approver` 未真正校验角色：有 `assignee` 才校验，无 assignee 且 `approver_role` 非空即 **return True**（`services/workflow/task.py:74-90`）；`create_tasks_for_start` 的 single 模式建的是 `assignee=None` 任务（`:57-69`）；order/purchase 默认流程末步就是 `StepDef(1,"manager")`（`services/workflow/resolver.py:107`）→ **任何管理端账号（含无业务权限的新用户）都能批准订单/采购** → ✅ **[已修复]**（P0-1：`check_available_approver` 按真实角色集合校验，无 assignee 时须角色匹配） |
| 审批留痕失真 | ① `ApprovalRecord.operator_role = task.approver_role`（`engine.py:129/170`）——不管操作人真实角色，一律记为流程角色（如 manager）；② 审批通过驱动下单时 `confirmed_by = 发起人`（`biz_hooks.py:85/100` 传 `inst.initiator_id`）→ 订单「确认人」记的是提交人而非审批人 → ✅ **[已修复]**（`operator_role` 优先取操作人真实角色码、`confirmed_by` 优先真实操作人，取不到才回退） |
| **转交无权限校验（高）** | `transfer_task` 不调用 `check_available_approver`，也不校验 `to_user_id` 租户/存在性（`engine.py:203-226`）→ 任意管理端用户可把任意待办转给自己后批准 → ✅ **[已修复]**（P0-1：校验操作人为当前审批人 + 目标用户为本租户启用用户） |
| 飞书回调缺验签 | `parse_event_body` 在无 `encrypt_key` 时原样放行，且全链路无 verification_token 校验（`services/feishu/callbacks.py:37-40`）；wecom（msg_signature）、dingtalk（robot 签名/card token）已验签 ✓ → ✅ **[已修复]**（P2-17：配置 `verification_token` 时强制校验回调 token，不匹配 403） |
| 导出任务越权读 | `export_jobs.py` 仅 admin portal 登录即可按 id 读任意导出任务（含薪资导出参数），配合 `/api/files/{id}` 租户级下载 → 同租户普通管理端用户可拿到薪资导出结果（缺权限码/owner 校验） → ✅ **[已修复]**（P2-18：`job_type` 权限码映射 + owner-or-permission 校验，未知类型 fail-closed） |
| H5 自校验 | ✓ h5/customer、tasks、report_units、temp_reports、attendance、salary_slips 均有角色/本人校验；注册接口有图形验证码 + 开关（`v1/tenants.py`） |
| 编号预览接口 | `system/codes.py` 仅 admin portal（GET 预览，影响低，可不改） |

### 2.8 工程风险

| 检查点 | 结论 |
| --- | --- |
| Alembic 链 | ✓ 91 个 migration，单一 head `0080_stock_checks`（P1/P2 新增 0075–0080 已执行落库），无 create_all 迁移（优于 cenkormes） |
| 启动开关 | ✅ **[已处理]** `backend/.env` 已切 `APP_ENV=prod` + `DB_AUTO_CREATE=false` + `DB_AUTO_SEED=false`（P3-26，重启后端后生效） |
| 测试 | ✅ **[已修复]** `date_format()` 已改可移植范围过滤、`utcnow()` 全库替换（P3-28）；全量 **312 passed / 0 failed**（内存 sqlite） |
| 版本一致性 | ✓ `VERSION` v1.2.0 与 `CHANGELOG.json` 最新条目一致（共 30 条） |
| 包内遗留备份 | ✅ **[已处理]** `BACKUP_fixclosure_20260905_*`（2 份）与 `app/BACKUP_temp_report_20260905_155255`（app 包内）已于 P3-27 统一归档至 `.local-backups/archive_20261006/`，工作区残留归零、无 import 风险 |
| 运行时文件入库 | ✅ **[已处理]** 备份文件已归档至 `.local-backups/archive_20261006/`（P3-27）；`.gitignore` 补 `*.bak*`/`BACKUP_*`/`dist_bak_*/`/`readme_backup_*/` 并将 `celerybeat-schedule` 升级为 `celerybeat-schedule*`；`celerybeat-schedule-{db,shm,wal}` 本地保留、建议 `git rm --cached` |
| 历史产物 | ✅ **[已处理]** `dist_bak_*` 已归档（P3-27）；仓库根 `*.tar.gz`/`*.sql`/`song_output.*` 已被 `.gitignore` 覆盖（本地保留，不入库） |
| community-patches | `scripts/community-patches/` 为社区版（AGPL）补丁目录，与主代码无引用关系；发布时注意 License 边界 |

---

## 第三部分：汇总与整改优先级

> 本部分汇总前置全部发现（含第一部分对照项），去重后按修复紧迫度排序。

### P0 立即修（越权 / 跨租户 / 账实不符）——✅ 6 项全部已修复（2026-10-06）

1. ✅ **[已修复] 工作流审批放行**：`check_available_approver` 角色未校验即放行 + `transfer_task` 无任何校验（`services/workflow/task.py:74-90`、`engine.py:203-226`）→ 任意管理端用户可审批/转交订单、采购；默认流程步为 `StepDef(1,"manager")`（resolver.py:107）。修复：审批前按用户真实角色集合与 `approver_role` 匹配；transfer 先校验操作人是当前审批人，且校验 to_user 为本租户启用用户。
2. ✅ **[已修复] 外协发料跨租户写入 + 超发**：`SubcontractSendIn.sends` 无类型（`schemas/subcontract.py:50`）+ `create_send_logs` 不校验 item 归属不控上限（`crud/subcontract.py:113-119`）。修复：改用强类型 schema（item_id/qty ge=1），查询加 `tenant_id`+`order_id` 约束，校验累计发料 ≤ 委外数量。
3. ✅ **[已修复] 库存三接口缺归属校验**：手工调整（`warehouse/router.py:138`）、入库单（`warehouse_entries.py:103`）、领料/退料（`crud/material_issue.py:58/160`）均需补 warehouse/sku/work_order/PO 的租户归属校验，并给 `adjust_stock` 加非负护栏与 `stocks.qty` CHECK。
4. ✅ **[已修复] 双重入库**：件次终审按件入库 + 工单完工全量入库重叠（`report_units.py:415-430` vs `crud/work_order.py:99-131`）。修复：单位报工模式下工单级入库跳过（或幂等检查同时识别 `biz_id=unit.id` 日志）。
5. ✅ **[已修复] 越权改钱**：补贴接口拆出专用权限（Part 1 #1）；`/reports/salary/*` 改挂 `salary.view`/`salary.manage`（`reports.py:25`）。
6. ✅ **[已修复] 对账重复计费**：销售/供应商两侧生成对账单时校验原单是否已入账（`api/admin/finance/router.py:300`、`crud/supplier_statement.py:112-151`），并将 period 必填或改为按未对账明细取数。

### P1 尽快修（财务口径与闭环缺口）

7. ✅ **[已修复]** H5 客户自助 `mark-paid` 改为“提交回款登记”（待财务核实）（`api/h5/customer.py:465-505`）。
8. ✅ **[已修复]** 发货外协账实：`shipments`/外协发料收回补 `warehouse_id` 并写库存流水（Part 1 #2/#3）。
9. ✅ **[已修复]** 工资落账 + 利润口径：`SalarySlip` 补四列发放字段 + 发放写 `FinanceLedger(labor)`；`profit_api` 成本加入人工成本并输出 `purchase_cost/labor_cost` 拆分（Part 1 #4、2.2）。
10. ✅ **[已修复]** 核销能力：新增 `statement_payments` 逐笔核销/部分收款/账龄；`mark-paid` 改差额核销（幂等+自愈）；前后端支持部分收款/付款登记（Part 1 #5）。
11. ✅ **[已修复]** 工资条签收快照锁定：已签收/已发放后 `ensure_salary_slip` 不再重算覆盖金额（`crud/salary_slip.py`）。
12. ✅ **[已修复]** 临时报工绑定：补派工上限 + 任务计划上限双重校验；绑定即终审写 `ReportAudit` 留痕（`api/admin/production/temp_reports.py`，公共累计口径抽至 `crud/task.py: sum_task_done_good_qty`）。
13. ✅ **[已修复]** 审核 SoD：新增 `assert_report_audit_sod` / `assert_unit_audit_sod` 公共校验（自审拦截 + 初审/终审不得同一人），覆盖 admin 报工/件次端点、IM 卡片、企微卡片与临时报工绑定 4 条通道（`crud/report.py`、`crud/report_unit.py`）。
14. ✅ **[已修复]** 外协结算落账：`settle` 按 `Σ(unit_price × received_qty)` 生成 `FinanceLedger(out/subcontract)` 应付流水（幂等 + 零金额不记账）；`profit_api` 成本并入外协成本 `subcontract_cost`（`api/admin/subcontract/router.py`、`api/admin/finance/router.py`）。
15. ✅ **[已修复]** 留痕补口：工资条重置、手工记账、订单驳回补写 `operation_logs`（手工调库存核对为已有实现并补回归测试）；失败路径不落日志（`api/admin/production/salary_reports.py`、`api/admin/finance/router.py`、`api/admin/production/orders.py`）。
16. ✅ **[已修复]** 退料超领护栏：`confirm_return` 校验领料单必须已实际领料（issued）+ 累计退料 ≤ 已领量；补「未领可退」缺口，库存/流水口径测试锁定（`crud/material_issue.py`）。

### P2 计划修

17. ✅ **[已修复]** 飞书事件回调验签：`verify_event_token` 校验回调 token（配置了 `verification_token` 才强制；防伪造事件与卡片回调），异常转 403（`services/feishu/callbacks.py`、`api/feishu/router.py`）。
18. ✅ **[已修复]** 导出任务越权读：`job_type` 权限码映射 + owner-or-permission 校验，未知类型 fail-closed（`api/admin/export_jobs.py`）。
19. ✅ **[已修复]** 通知未注册事件不静默：`dispatch` 结尾记 warning 告警（不抛异常），含 `event_code/tenant_id/title`（`notify_dispatcher.py`）。
20. ✅ **[已修复]** MRP：库存汇总过滤停用仓（`sum_stock_qty_by_sku_ids` join `Warehouse.is_active`，MRP/齐套/领料统一口径）；convert 支持按供应商分单（留空自动按物料默认供应商分单）；另修复前端 `run/convert` query/body 传参错位与 MRP 页面 i18n 缺段；前端遗留已闭环：`MrpRunsPage/MrpResultPage` 补注册路由（`mrp/runs`、`mrp/runs/:id`，name `mrp-runs`/`mrp-result`，权限 `mrp.run`）+ 生产菜单项（`menu.mrp`），vue-tsc 通过。
21. ✅ **[已修复]** 库存盘点闭环：`stock_checks`/`stock_check_items` 两表 + 6 端点（全盘/抽盘建单快照 → 实盘录入 → 完成时按差异自动调库存并写 `stock_check` 流水，完成后锁定、完成写操作留痕）；前端「库存盘点」页面（`api/admin/warehouse/stock_checks.py`、`crud/stock_check.py`、`pages/warehouse/StockChecksPage.vue`）。
22. ✅ **[已修复]** `cron_jobs` 双模式收敛：新增平台端 `/api/platform/cron-jobs`（挂平台超管），SaaS 模式下 admin 写操作 403（GET 只读），私有化模式保持可写（`api/platform/cron_jobs.py`、`api/admin/cron_jobs.py`、`crud/cron_job.py`；前端平台后台页面 + 租户页 SaaS 只读提示）。
23. ✅ **[已修复]** 采购作废：`cancel` 补 `reason`（写入 `operation_logs.detail`）；`partial_received` 作废 reason 必填（400，防掩盖已收货事实）（`purchase/orders.py`）。
24. ✅ **[已修复]** 金额口径统一：`scan_order_statement` 统一扫描（金额+问题列表不抛异常），`POST /finance` 聚合列出全部缺价订单后一次性 400（附修复指引），新增 `GET /statements/precheck` 预检端点（不写库不阻断；`crud/finance.py`、`api/admin/finance/router.py`）。
25. ✅ **[已修复]** `leader-approve` 补行锁：`get_report_by_id(for_update=True)`（`api/admin/production/reports.py`）。

### P3 工程卫生（5/5 完成）

26. ✅ **[已修复]** 环境切换：`backend/.env` 改 `APP_ENV=prod`（500 错误不再暴露堆栈详情）、`DB_AUTO_CREATE=false`、`DB_AUTO_SEED=false`（JWT_SECRET 已达标不拦截启动；新建租户角色初始化不受影响——`create_default_roles_for_tenant` 在租户创建流程内调用）。今后新迁移用 `alembic upgrade head`；新增权限码后手动跑一次 `ensure_permissions` + `ensure_default_roles_all_tenants`（或重启一次）。需重启后端生效（用户手动）。
27. ✅ **[已修复]** 备份清理：约 280 项历史备份（`.bak_*` / `BACKUP_*` / `dist_bak_*` / `readme_backup_*`，含 `app` 包内 `BACKUP_temp_report_*` 目录）统一归档至 `.local-backups/archive_20261006/`（保留相对路径，共 1323 个文件，工作区残留归零）；`.gitignore` 补 `*.bak` / `*.bak_*` / `*.bak.*` / `BACKUP_*` / `dist_bak_*/` / `readme_backup_*/`，并将 `celerybeat-schedule` 升级为 `celerybeat-schedule*`。277 个已跟踪文件随下次 commit 自然出库；`backend/celerybeat-schedule-{db,shm,wal}` 为运行时文件（本地保留），建议 `git rm --cached` 移出索引。
28. ✅ **[已修复]** `date_format()` 改可移植写法：`reports/purchase.py`、`ai/contexts/factory_extended.py` 改「`>= 月初 AND < 下月初`」范围过滤（新增 `app/utils/dates.py::month_range`，非法月份保持空结果语义）；`utcnow()` 弃用清理：50 处全库替换为 `app/utils/dates.py::utcnow()`（naive UTC 语义等价）+ 冗余 import 清理 15 文件；顺带修正 `test_boss_qa_mock` mock 目标（模块级 from import 须打在 `app.services.ai.scenes.chat_completion`）。新增 `tests/test_month_range.py`（11）。全量 **312 passed / 0 failed（全绿）**。
29. ✅ **[已修复]** 删除 `plans.py` 重复路由定义（原 `:1751-1788`：forecast / aps-strategy 各 2 份 → 各 1 份；函数 4 → 2）。
30. ✅ **[已修复]** 空转权限码清零：`tenant.manage` / `report.submit` / `report.work_self` 从 `seed.py` 删除（`salary.view` 已在 P0-5 接线），`leader` / `employee` 角色预设同步移除；小程序 `permissions.ts` 删 `REPORT_SUBMIT` 常量；`salary.ts` 重复 allowances 包装删除。权限扫描双空 + 全量测试通过 + `vue-tsc` 通过。
31. ✅ **[已修复]**（审计收尾补口）发货取消端点：新增 `POST /admin/warehouse/shipments/{id}/cancel`——pending 直接取消（未扣库存）；shipped 取消时逐项回滚库存 + 写 `ship_cancel` 冲销流水，订单无其它有效发货单（shipped/signed）时状态回退 `confirmed`；signed 不可取消（400）；重复取消 400；`operation_logs` 留痕；前端发货页取消按钮 + `statusCancelled` 状态映射 + 双语 i18n。新增 `tests/test_shipment_cancel.py`（5），全量 **312 passed / 0 failed**。

> 审计脚本留存：`backend/_audit_perm_scan.py`（权限覆盖扫描，可重复运行回归）。
