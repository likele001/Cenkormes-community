# LightMes 管理后台 UI 约定

本文档描述 `frontend-admin-pro` 统一页面模板与设计系统的使用方式。新页面与改造旧页时请遵循以下约定。

## 设计系统

- 全局 CSS 变量定义在 `src/style.css`（`:root` / `.dark`）。
- 主题切换：`useAdminTheme()`，在 `main.ts` 初始化；顶栏按钮切换明暗模式。
- **禁止**在页面内硬编码 `#409eff`、`#303133` 等色值，改用：
  - `var(--el-color-primary)`
  - `var(--el-text-color-primary)`
  - `var(--admin-brand-subtitle)` 等 token

## 布局壳层

- 租户后台：`AppLayout.vue`（侧栏折叠、品牌区、顶栏工具）
- 平台后台：`PlatformLayout.vue`（视觉与 AppLayout 对齐）
- 品牌组件：`AdminBrand.vue`（租户 `logo_url` + `tenant_name`，无 Logo 时 fallback `LM`）

## 页面容器

### AdminPage

所有业务页（列表、表单、详情）外层使用 `AdminPage`：

```vue
<AdminPage title="产品" description="可选副标题">
  <template #actions>
    <!-- 筛选、新建等操作按钮 -->
  </template>

  <!-- 主内容区 -->

  <template #extra>
    <!-- 弹窗、抽屉等不占主布局的浮层 -->
  </template>
</AdminPage>
```

例外：登录/注册页（`LoginPage`、`JoinPage`）、平台登录页、纯全屏页（如车间大屏可保留自定义根节点，但仍建议包一层 `AdminPage` 统一标题）。

### AdminDataTable

标准列表页（桌面表格 + 移动卡片 + 分页）使用：

```vue
<AdminDataTable
  :loading="loading"
  :empty="!loading && !items.length"
  :page-size="query.limit"
  :total="fakeTotal"
  :current-page="page"
  @page-change="onPageChange"
>
  <template #table>
    <el-table class="hidden lg:block w-full" :data="items" border>
      <!-- columns -->
    </el-table>
  </template>
  <template #mobile>
    <div class="lg:hidden space-y-3">
      <div v-for="row in items" :key="row.id" class="admin-mobile-row">
        <!-- admin-mobile-row__head / admin-mobile-kv / admin-mobile-actions -->
      </div>
    </div>
  </template>
</AdminDataTable>
```

空态由 `AdminDataTable` 内置 `AdminEmpty` 处理，移动区无需再写 `el-empty`。

### AdminFilterBar

复杂筛选区可单独使用 `AdminFilterBar`（窄屏自动换行，样式见 `style.css`）。

### AdminEmpty / AdminPageSkeleton

- 非表格场景的空态：`AdminEmpty`
- 首屏加载：`AdminPageSkeleton`

## 列表逻辑

推荐使用 `useListPage` 收拢分页与 `reload` 样板代码（见 `ProductsPage.vue`、`OrdersPage.vue`）。

## 响应式断点

- **1024px**：侧栏抽屉模式（`style.css` 中 `@media (max-width: 1023px)`）
- **lg (1024px)**：表格与移动卡片切换（`hidden lg:block` / `lg:hidden`）

## 参考实现

| 页面 | 说明 |
|------|------|
| `ProductsPage.vue` | AdminPage + AdminDataTable + useListPage 完整范例 |
| `OrdersPage.vue` | 多操作列 + 复杂弹窗放 `#extra` |
| `UsersPage.vue` | 系统管理列表试点 |
| `HomePage.vue` | 仪表盘：AdminPage 标题区 + 保留原有图表卡片 |

## 构建与发布

```bash
cd frontend-admin-pro
npm run check
npm run build
```

产物目录 `dist/` 部署至宝塔 admin 站点（见 `docs/三站点前端宝塔配置方案.md`）。
