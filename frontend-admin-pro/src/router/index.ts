import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { i18n } from '@/locales'

import { getH5PortalKind, redirectToH5Portal } from '@/utils/h5-entry'
import { getStoredTenantCode, parseTenantFromPath, setStoredTenantCode, tenantAdminPath } from '@/utils/tenant'
import { tryRecoverStaleChunk } from '@/utils/chunk-reload'

/** 社区版路由：不含 CRM、工资、财务、采购、仓储、平台、AI 等 Pro 页面 */
const appChildren: RouteRecordRaw[] = [
  { path: '', redirect: 'home' },
  { path: 'home', name: 'home', component: () => import('@/pages/HomePage.vue'), meta: { title: () => i18n.global.t('menu.home'), permissions: ['dashboard.view'] } },

  { path: 'system/users', name: 'system-users', component: () => import('@/pages/system/UsersPage.vue'), meta: { title: () => i18n.global.t('menu.users'), permissions: ['user.manage'] } },
  { path: 'system/roles', name: 'system-roles', component: () => import('@/pages/system/RolesPage.vue'), meta: { title: () => i18n.global.t('menu.roles'), permissions: ['role.manage'] } },
  { path: 'system/permissions', name: 'system-permissions', component: () => import('@/pages/system/PermissionsPage.vue'), meta: { title: () => i18n.global.t('menu.permissions'), permissions: ['permission.manage'] } },
  { path: 'system/departments', name: 'system-departments', component: () => import('@/pages/system/DepartmentsPage.vue'), meta: { title: () => i18n.global.t('menu.departments'), permissions: ['department.manage'] } },
  { path: 'system/settings', name: 'system-settings', component: () => import('@/pages/system/SettingsPage.vue'), meta: { title: () => i18n.global.t('menu.settings'), permissions: ['setting.manage'] } },
  { path: 'system/notifications', name: 'system-notifications', component: () => import('@/pages/system/NotificationsPage.vue'), meta: { title: () => i18n.global.t('menu.notifications'), permissions: ['notification.view'] } },
  { path: 'system/dictionary', name: 'system-dictionary', component: () => import('@/pages/system/DictionaryPage.vue'), meta: { title: () => i18n.global.t('menu.dictionary'), permissions: ['dict.manage'] } },
  { path: 'system/attachments', name: 'system-attachments', component: () => import('@/pages/system/AttachmentsPage.vue'), meta: { title: () => i18n.global.t('menu.attachments'), permissions: ['attachment.view'] } },
  { path: 'account/profile', name: 'account-profile', component: () => import('@/pages/account/ProfilePage.vue'), meta: { title: () => i18n.global.t('menu.profile') } },

  { path: 'master/products', name: 'master-products', component: () => import('@/pages/master/ProductsPage.vue'), meta: { title: () => i18n.global.t('menu.products'), permissions: ['product.manage'] } },
  { path: 'master/skus', name: 'master-skus', component: () => import('@/pages/master/SkusPage.vue'), meta: { title: () => i18n.global.t('menu.skus'), permissions: ['sku.manage'] } },
  { path: 'master/processes', name: 'master-processes', component: () => import('@/pages/master/ProcessesPage.vue'), meta: { title: () => i18n.global.t('menu.processes'), permissions: ['process.manage'] } },
  { path: 'master/process-routes', name: 'master-process-routes', component: () => import('@/pages/master/ProcessRoutesPage.vue'), meta: { title: () => i18n.global.t('menu.processRoutes'), permissions: ['product.manage'] } },

  { path: 'production/orders', name: 'production-orders', component: () => import('@/pages/production/OrdersPage.vue'), meta: { title: () => i18n.global.t('menu.orders'), permissions: ['order.manage'] } },
  { path: 'production/work-orders', name: 'production-work-orders', component: () => import('@/pages/production/WorkOrdersPage.vue'), meta: { title: () => i18n.global.t('menu.workOrders'), permissions: ['work.manage'] } },
  { path: 'production/tasks', name: 'production-tasks', component: () => import('@/pages/production/TasksPage.vue'), meta: { title: () => i18n.global.t('menu.tasks'), permissions: ['task.manage', 'dispatch.manage'] } },
  { path: 'production/assignments', name: 'production-assignments', component: () => import('@/pages/production/AssignmentsPage.vue'), meta: { title: () => i18n.global.t('menu.assignments'), permissions: ['dispatch.manage'] } },
  { path: 'production/inspection-templates', name: 'production-inspection-templates', component: () => import('@/pages/production/InspectionTemplatesPage.vue'), meta: { title: () => i18n.global.t('menu.inspectionTemplates'), permissions: ['report.audit'] } },
  { path: 'production/defect-codes', name: 'production-defect-codes', component: () => import('@/pages/production/DefectCodesPage.vue'), meta: { title: () => i18n.global.t('menu.defectCodes'), permissions: ['report.audit'] } },
  { path: 'production/reports', name: 'production-reports', component: () => import('@/pages/production/ReportsPage.vue'), meta: { title: () => i18n.global.t('menu.reports'), permissions: ['report.audit'] } },

  { path: ':pathMatch(.*)*', name: 'adminNotFound', redirect: (to) => `/t/${String(to.params.tenantCode)}/home` },
]

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/pages/LoginPage.vue'), meta: { public: true, title: () => i18n.global.t('menu.login') } },
  { path: '/t/:tenantCode/login', name: 'tenant-login', component: () => import('@/pages/LoginPage.vue'), meta: { public: true, title: () => i18n.global.t('menu.login') } },
  {
    path: '/t/:tenantCode',
    component: () => import('@/layouts/AppLayout.vue'),
    redirect: (to) => `/t/${String(to.params.tenantCode)}/home`,
    children: appChildren,
  },
  {
    path: '/',
    redirect: () => {
      const code = getStoredTenantCode()
      return code ? `/t/${code}/home` : '/login'
    },
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const pathTenant =
    parseTenantFromPath(to.path) ||
    (typeof to.params.tenantCode === 'string' ? to.params.tenantCode.toUpperCase() : null)

  const auth = useAuthStore()
  const isPublic = Boolean(to.meta.public)
  if (isPublic) {
    if (pathTenant) setStoredTenantCode(pathTenant)
    return true
  }

  const loginPath = pathTenant ? `/t/${pathTenant}/login` : '/login'
  if (!auth.token) {
    if (pathTenant) setStoredTenantCode(pathTenant)
    return { path: loginPath, query: { redirect: to.fullPath } }
  }

  if (!auth.me) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { path: loginPath, query: { redirect: to.fullPath } }
    }
  }

  const sessionTenant = (auth.me?.tenant_code || getStoredTenantCode() || pathTenant || '').trim().toUpperCase()
  if (sessionTenant) setStoredTenantCode(sessionTenant)

  if (pathTenant && sessionTenant && pathTenant !== sessionTenant) {
    const sub = to.path.replace(/^\/t\/[^/]+/i, '') || '/home'
    return `/t/${encodeURIComponent(sessionTenant)}${sub.startsWith('/') ? sub : `/${sub}`}`
  }

  if (!parseTenantFromPath(to.path) && sessionTenant) {
    return tenantAdminPath(to.path, sessionTenant)
  }

  const h5Kind = auth.me ? getH5PortalKind(auth.me) : null
  if (h5Kind) {
    const tc = (sessionTenant || pathTenant || '').trim()
    if (tc && (await redirectToH5Portal(tc, h5Kind))) {
      auth.logout()
      return false
    }
    auth.logout()
    ElMessage.warning('员工请使用手机端 H5 报工')
    return { path: loginPath }
  }

  const need = to.meta.permissions as string[] | undefined
  const optional = new Set(['dashboard.view'])
  const required = need?.filter((x) => !optional.has(x))
  if (required && required.length > 0 && !auth.hasAnyPermission(required)) {
    ElMessage.error('无权限访问')
    return tenantAdminPath('/home', sessionTenant || getStoredTenantCode())
  }
  return true
})

router.onError((error) => {
  tryRecoverStaleChunk(error)
})

export default router
