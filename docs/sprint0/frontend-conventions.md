# LightMes 前端开发规范（Sprint 0）

> 本规范于 Sprint 0（2026-06-23 ~ 2026-07-04）建立，Sprint 1-3 所有新功能需遵循此规范。

---

## 1. 列表页模板

所有列表页遵循统一结构：

```
AdminPage
  └─ AdminFilterBar (筛选 + 搜索/重置/导出按钮)
       ├─ default slot: 筛选控件（el-input / el-select / el-date-picker）
       └─ extra slot:  操作按钮（新建/导入等）
  └─ AdminDataTable
       ├─ table slot: el-table
       ├─ mobile slot: 窄屏卡片列表
       └─ emptyAction slot: 空状态引导按钮（通过 AdminEmpty props 传入）
  └─ AdminActionMenu (操作列收纳)
       ├─ primaryActions: 主操作按钮(1-2 个)
       └─ moreActions: 下拉菜单收纳次要操作
```

参考文件：
- `components/admin/AdminPage.vue`
- `components/admin/AdminFilterBar.vue`
- `components/admin/AdminDataTable.vue`
- `components/admin/AdminEmpty.vue`
- `components/admin/AdminActionMenu.vue`

---

## 2. 状态显示 — 必须用 useStatus()

**禁止**在页面内定义 `statusLabel()` / `statusType()` / `statusMap` / `statusColors`。

```typescript
// ✅ 正确
import { useStatus } from '@/utils/status-maps'
const { label: statusLabel, type: statusTagType } = useStatus('order')

// 模板
<el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
```

**可用 domain**（`src/utils/status-maps.ts` 定义）：

| domain | 适用模块 |
|--------|---------|
| `order` | 订单 |
| `work_order` | 工单 |
| `task` | 任务 |
| `report` | 批量报工 |
| `report_unit` | 件次报工 |
| `purchase_order` | 采购单 |
| `purchase_statement` | 采购对账单 |
| `customer_statement` | 客户对账单 |
| `crm_opportunity` | CRM 商机 |
| `equipment` | 设备 |
| `shipment` | 发货 |
| `plan` | 生产计划 |
| `assignment` | 分工分配 |

---

## 3. 颜色 — 必须用 CSS 变量

**禁止**使用 `text-[#xxx]` / `bg-[#xxx]` / `border-[#xxx]` 等 Tailwind 任意值硬编码。

| 替代类 | 对应 CSS 变量 | 用途 |
|--------|-------------|------|
| `text-el-primary` | `var(--el-text-color-primary)` | 主文字色 |
| `text-el-regular` | `var(--el-text-color-regular)` | 常规文字色 |
| `text-el-placeholder` | `var(--el-text-color-placeholder)` | 辅助/占位文字色 |
| `bg-el-fill` | `var(--el-fill-color-light)` | 填充背景色 |
| `border-el-primary` | `var(--el-color-primary)` | 主边框色 |

---

## 4. 需额外 CSS 变量的场景

对于状态色 / 品牌色，reference `style.css` 中的 `:root` 变量：

```css
color: var(--el-color-primary);        /* 品牌蓝 */
color: var(--el-color-success);         /* 绿色 */
color: var(--el-color-warning);         /* 橙色 */
color: var(--el-color-danger);          /* 红色 */
color: var(--el-color-info);            /* 灰色 */
```

**TV 大屏**使用独立的 `--tv-*` 变量系列（定义在 `style.css`），不受 admin 暗色模式影响。

---

## 5. 复杂表单 — 必须启用 useUnsavedGuard

```typescript
import { useUnsavedGuard } from '@/composables/useUnsavedGuard'

const { isDirty, markDirty, markClean, saveToStorage, loadFromStorage } = useUnsavedGuard('form-key')

// 表单字段变化时调用 markDirty()
// 保存成功后调用 markClean()
```

- 离开页面时弹出确认（`beforeRouteLeave`）
- 关闭/刷新浏览器时弹出确认（`beforeunload`）
- 表单自动存入 `sessionStorage`，下次打开可恢复

---

## 6. 空状态 — 必须配置引导操作

```vue
<!-- 通过 AdminEmpty props 传入引导按钮 -->
<AdminEmpty
  :createText="t('common.create')"
  :createAction="handleCreate"
  :importText="t('common.import')"
  :importAction="handleImport"
  :guideText="t('common.guide')"
  :guideAction="handleGuide"
/>

<!-- 或通过 action slot 自定义 -->
<AdminEmpty>
  <template #action>
    <el-button>自定义操作</el-button>
  </template>
</AdminEmpty>
```

---

## 7. 暗色模式

- `html.dark` 由 `useAdminTheme` composable 自动控制
- 所有 Element Plus 组件自动适配
- 自定义组件颜色必须使用 CSS 变量（`var(--el-*)`）
- TV 大屏（`.tv-screen`）独立主题，不受暗色模式影响

---

## 8. Git 操作

在修改前端文件前，先运行备份脚本：

```bash
# 创建带时间戳的备份
bash scripts/backup_frontend.sh

# 创建/更新快照（增量开发时使用）
bash scripts/backup_frontend.sh snapshot

# 从备份还原
bash scripts/backup_frontend.sh restore /www/backups/lightmes/frontend/pre-sprint0_20260614_043711
```

---

*本规范于 Sprint 0 结束时由用户评审确认，Sprint 1-3 及后续开发均需遵守。*
