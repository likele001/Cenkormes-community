# LightMes / CenkorMES 知识库规划方案（v2 · 含技术开发文档区）

> 目标：新建 `/www/wwwroot/lightmes/knowledge/`，把现有零散 `docs` 归类为 **业务/运维区**，并**新增完整的技术开发文档区**（二次开发指南、每个 API、数据模型、数据库结构），形成"能学习、能上手二次开发"的项目知识库。

---

## 〇、后端真实结构（基于服务器实测）

这套体系是 **模块化 FastAPI 后端**，二次开发文档就围绕它组织：

| 层 | 实际内容（实测） |
|----|----------------|
| **核心配置 core/** | config、db、deps、edition、errors、package_gate、portal_access、redis_client、response、security、seed |
| **API 入口 api/** | router.py 注册 davhboard/feishu/platform/wecom/dingtalk/h5/miniapp/payment/public/v1/ws |
| **管理后台 api/admin/** | ai、ai_employee、approval、assistant、automation、dictionary、equipment、erp、finance、industry、master、mold、mrp、production、purchase、quotation、reports、shift、spc、subcontract、system、trace、warehouse、workflow 等 |
| **数据模型 models/** | **81 个模型文件**，按 主数据/生产/ERP/质量/薪酬/平台/SaaS 等域划分 |
| **服务层 services/** | ai、ai_employee、feishu、wecom、dingtalk、wechat_mp、workflow、abac、assistant |
| **行业包 industries/** | food、auto_parts、electronics、injection_molding、garment、machining |

API 前缀约定：后台模块走 `/api/admin/*`，业务有 `/api/v1/*`、`/api/h5/*`、`/api/miniapp/*`。

---

## 一、现状盘点（0 → docs 归类）

项目有 **3 处 docs**（`docs/`、`community/docs/`、`pro-build/docs/`），内容重复（根 docs 最全）。现有 `docs/` 内容 6 类：

| 类别 | 示例 | 数量级 |
|------|------|--------|
| 部署与运维 | Docker部署指南、宝塔部署、Celery与消息推送、飞书/钉钉/企微推送、服务器迁移 | ~12 |
| 操作手册/SOP | 生产自动化操作手册、AI智能工厂SOP、设备管理、小程序使用、操作教程 | ~10 |
| 产品与方案 | 产品宣传册、套餐规划、官网文案、公众号文案、demo-video、完整闭环说明 | ~8 |
| 开发约定 | frontend-conventions、admin-ui-conventions、Git双仓库发布、AI集成说明 | ~8 |
| 临时/内部 | 待办事项、迁移操作日志、就看一次、本地测试包说明 | ~5 |
| 素材资产 | screenshots/（大量截图）、screenshots.tar.gz | 大量 |

> ⚠️ 用户重点强调：知识库必须包含**二次开发技术文档**（每个 API、数据模型、数据库结构介绍）。v2 把这类扩展为独立「技术开发区」。

---

## 二、目标目录结构（knowledge/）

```
/www/wwwroot/lightmes/knowledge/
├── README.md                        ← 总索引（业务导航 + 开发者导航）
│
├── 【业务与运维区】
├── 04-部署与运维/
│   ├── 部署指南.md                   （Docker/宝塔/服务器迁移 合并）
│   ├── 常见问题排查.md
│   └── 消息推送配置.md               （飞书/企微/钉钉 合并）
├── 05-操作手册-SOP/
│   ├── 生产自动化操作手册.md
│   ├── AI智能工厂SOP.md
│   ├── 小程序使用指南.md
│   └── 设备管理操作指南.md
├── 06-开发约定/
│   ├── 前端规范.md
│   ├── Git与双仓库发布.md
│   └── 品牌与三方可声明.md
├── 07-产品与方案/
│   ├── 宣传与官网文案.md
│   └── 套餐与版本规划.md
│
├── 【技术开发文档区】★新增 用户重点
├── 20-技术架构/
│   ├── 总体架构.md                   （请求链路、前后端、服务边界）
│   ├── 后端模块总览.md               （core/services/api 职责）
│   ├── 权限与ABAC.md
│   ├── SaaS多租户隔离.md
│   └── 消息推送架构.md
├── 21-二次开发指南/
│   ├── 新增一个业务模块.md           （路由注册 → install_app → 权限 → 菜单）
│   ├── 新增一个数据模型+迁移.md      （models → alembic，幂等规则）
│   ├── 前端二次开发.md
│   └── 发布与打包流程.md             （pack.sh / build.sh / release-all）
├── 22-API参考/                       ← 每个接口
│   ├── README-接口总索引.md
│   ├── 认证与租户.md
│   ├── 主数据-设备/物料/工序/工艺.md
│   ├── 生产-工单/报工/计划/MRP.md
│   ├── ERP-采购/销售/财务/库存/发货.md
│   ├── 质量-SPC/质检/售后.md
│   ├── 薪酬-工资条/考勤.md
│   ├── AI-AI员工/AI集成/识别.md
│   ├── 审批-工作流/报表.md
│   ├── 消息推送-飞书/企微/钉钉.md
│   └── 运维-系统/版本/导出/定时任务.md
├── 23-数据模型/                      ← 118→ 每个模型
│   ├── README-数据模型总索引.md      （81 模型按域列清单）
│   ├── 主数据域.md                   （customer/product/material/equipment/process/sku...）
│   ├── 生产域.md                     （work_order/report_unit/production_plan/task...）
│   ├── ERP域.md                      （purchase/shipment/invoice/ledger/asset/cost...）
│   ├── 质量·薪酬域.md                （spc/quality/salary/salary_slip/attendance...）
│   └── 平台·SaaS域.md                （tenant/user/role/permission/saas_package...）
├── 24-数据库结构/
│   ├── ER总览.md
│   ├── 表清单.md                     （表名 + 用途 + 所属域）
│   ├── 迁移链说明.md                 （0001→0002→0003 / ERP迁移链）
│   └── 关键表结构说明.md
│
├── 【共享】
├── 08-踩坑档案/
│   ├── README.md
│   └── 0001-missing-greenlet.md ...
└── templates/
    ├── README.md
    ├── 文档模板.md
    ├── 踩坑记录模板.md
    ├── API接口模板.md
    └── 数据模型模板.md
```

---

## 三、API / 模型 / 数据库文档怎么产出（可持续方案）

| 文档 | 产出方式 | 说明 |
|------|---------|------|
| **API 参考** | 优先从 FastAPI `openapi.json` 自动生成基线 → 人工补参数说明与示例 | 后端是 FastAPI，`/openapi.json` 可直接导出每个接口的路径/方法/请求/响应 schema，保证覆盖全且不脱节 |
| **数据模型** | 按 81 个模型文件按域归类，每个模型写「用途 + 关键字段 + 关系」 | 从 `backend/app/models/*.py` 派生 |
| **数据库结构** | ER 总览 + 表清单 + 迁移链 | 从 alembic versions 与 models 派生 |
| **二次开发指南** | 手工编写，沉淀 3 个典型场景 | 新增模块 / 新增模型+迁移 / 发布打包 |

> 建议首次生成用脚本批量导出 openapi.json 与 models 清单，之后靠模板维护增量，避免手写全部导致漏同步。

---

## 四、README 总索引（导航）模板

```markdown
# CenkorMES 知识库

📦 LightMes(社区) + CenkorMES(商业) 轻量化生产管理系统

## 🖥️ 我只会用（业务与运维）
- 🚀 [部署与运维](04-部署与运维/)
- 📘 [操作手册](05-操作手册-SOP/)

## 👨‍💻 我要二次开发（技术文档）
- 🏗️ [技术架构](20-技术架构/)
- 🔧 [二次开发指南](21-二次开发指南/)  ← 新手指引：怎么加模块/加模型/发布
- 🔌 [API 参考](22-API参考/)            ← 每个接口
- 🗄️ [数据模型](23-数据模型/)           ← 每个模型
- 💾 [数据库结构](24-数据库结构/)        ← 表与 ER

## 🔍 排障
- 🐛 [踩坑档案](08-踩坑档案/)  ← 每次报错必查
```

---

## 五、文档模板规范（写入 templates/）

### 1. API 接口模板
```markdown
# <模块> · <接口名>
- 路径：`/api/admin/xxx/...`
- 方法：GET/POST/PUT/DELETE
- 权限：需要哪些 role / 是否租户隔离
- 请求参数：| 字段 | 类型 | 必填 | 说明 |
- 响应示例：```json {...}```
- 注意事项：脱敏/冷却/幂等/并发锁
```

### 2. 数据模型模板
```markdown
# <模型名>（表 <表名>）
- 所属域：主数据/生产/ERP/质量薪酬/平台SaaS
- 用途：
- 关键字段：| 字段 | 类型 | 说明 |
- 关系：(所属方/依赖方)
- 迁移：对应 migration id
```

### 3. 踩坑记录模板
```markdown
# <序号>- 一句话标题
- 日期/模块/严重度
## 症状 → ## 根因 → ## 解决方案 → ## 涉及文件 → ## 预防
```

---

## 六、执行步骤（待确认后执行）

1. 创建 `knowledge/` 骨架（业务运维区 + 技术开发区 + templates/ + 踩坑档案/）
2. 写 `README.md` 总索引（含业务入口 + 开发者入口）
3. 复制 `docs/` 现有文件到业务运维区对应位置（保留原 docs，零风险）
4. 从后端批量导出 `openapi.json`、81 模型清单、表清单，生成 API/模型/表索引基线
5. 写二次开发指南（新增模块 / 新增模型+迁移 / 发布打包 3 篇）
6. 写入模板文件并校验链接与截图路径

> ⚠️ 采用「复制 + 保留原 docs」零风险迁移；你确认后可再清理旧 docs。