import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { tryRecoverStaleChunk } from '@/utils/chunk-reload'
import LoginPage from '@/pages/LoginPage.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import TasksPage from '@/pages/TasksPage.vue'
import TaskDetailPage from '@/pages/TaskDetailPage.vue'
import ReportWorkPage from '@/pages/ReportWorkPage.vue'
import WagesPage from '@/pages/WagesPage.vue'
import SalarySlipPage from '@/pages/SalarySlipPage.vue'
import AttendancePage from '@/pages/AttendancePage.vue'
import NotificationsPage from '@/pages/NotificationsPage.vue'
import CustomerOrderPage from '@/pages/CustomerOrderPage.vue'
import CustomerOrderDetailPage from '@/pages/CustomerOrderDetailPage.vue'
import CustomerOrderProgressPage from '@/pages/CustomerOrderProgressPage.vue'
import CustomerStatementsPage from '@/pages/CustomerStatementsPage.vue'
import CustomerStatementDetailPage from '@/pages/CustomerStatementDetailPage.vue'
import { i18n } from '@/locales'
import { useAuthStore } from '@/stores/auth'
import {
  fixDuplicateH5Path,
  getStoredTenantCode,
  parseTenantFromPath,
  setStoredTenantCode,
  stripTenantPrefix,
  tenantH5Path,
} from '@/utils/tenant'

const mainChildren: RouteRecordRaw[] = [
  { path: 'home', name: 'home', component: () => import('@/pages/HomePage.vue'), meta: { title: '首页' } },
  { path: 'screen', name: 'screen', component: () => import('@/pages/ScreenPage.vue'), meta: { title: '生产看板' } },
  { path: 'tasks', name: 'tasks', component: TasksPage, meta: { title: '我的任务' } },
  { path: 'tasks/:id', name: 'taskDetail', component: TaskDetailPage, meta: { title: '任务详情' } },
  { path: 'report', name: 'report', component: ReportWorkPage, meta: { title: '扫码报工' } },
  { path: 'report-unit', name: 'reportUnit', component: () => import('@/pages/ReportUnitPage.vue'), meta: { title: '逐件报工' } },
  { path: 'report-manual', name: 'reportManual', component: () => import('@/pages/ReportManualPage.vue'), meta: { title: '主动报工' } },
  { path: 'report-history', name: 'reportHistory', component: () => import('@/pages/ReportHistoryPage.vue'), meta: { title: '报工记录' } },
  { path: 'attendance', name: 'attendance', component: AttendancePage, meta: { title: '考勤打卡' } },
  { path: 'wages', name: 'wages', component: WagesPage, meta: { title: '我的工资' } },
  { path: 'salary/slip', name: 'salarySlip', component: SalarySlipPage, meta: { title: '电子工资条' } },
  { path: 'notifications', name: 'notifications', component: NotificationsPage, meta: { title: '消息中心' } },
  { path: 'profile', name: 'profile', component: () => import('@/pages/ProfilePage.vue'), meta: { titleKey: 'layout.profile' } },
  { path: 'help', name: 'help', component: () => import('@/pages/HelpPage.vue'), meta: { title: '智能帮助' } },
  { path: 'ai-hub', name: 'aiHub', component: () => import('@/pages/AiHubPage.vue'), meta: { title: '智能中心' } },
  { path: 'ai-alerts', name: 'aiAlerts', component: () => import('@/pages/AiAlertsPage.vue'), meta: { title: '数据预警', permissions: ['ai.alert.view'] } },
  { path: 'ai-assistant', name: 'aiAssistant', component: () => import('@/pages/AiAssistantPage.vue'), meta: { title: '工厂助手', permissions: ['ai.use'] } },
  { path: 'ai-employees', name: 'aiEmployees', component: () => import('@/pages/AiEmployeeListPage.vue'), meta: { title: 'AI 员工', permissions: ['ai_employee.use'] } },
  { path: 'ai-employees/:id/chat', name: 'aiEmployeeChat', component: () => import('@/pages/AiEmployeeChatPage.vue'), meta: { title: 'AI 员工对话', permissions: ['ai_employee.use'] } },
  { path: 'customer', redirect: { name: 'customerOrder' } },
  {
    path: 'customer/order',
    name: 'customerOrder',
    component: CustomerOrderPage,
    meta: { titleKey: 'customer.order.title' },
  },
  {
    path: 'customer/orders/:id',
    name: 'customerOrderDetail',
    component: CustomerOrderDetailPage,
    meta: { titleKey: 'customer.orderDetail.title' },
  },
  {
    path: 'customer/orders/:id/progress',
    name: 'customerOrderProgress',
    component: CustomerOrderProgressPage,
    meta: { titleKey: 'customer.orderProgress.title' },
  },
  {
    path: 'customer/statements',
    name: 'customerStatements',
    component: CustomerStatementsPage,
    meta: { titleKey: 'customer.statements.title' },
  },
  {
    path: 'customer/statements/:id',
    name: 'customerStatementDetail',
    component: CustomerStatementDetailPage,
    meta: { titleKey: 'customer.statementDetail.title' },
  },
  {
    path: ':pathMatch(.*)*',
    name: 'h5NotFound',
    redirect: (to) => `/t/${String(to.params.tenantCode)}/home`,
  },
]

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: () => { const code = getStoredTenantCode(); return code ? `/t/${code}/home` : '/login' } },
  { path: '/login', name: 'login', component: LoginPage, meta: { public: true, title: '登录' } },
  {
    path: '/guide',
    name: 'guide',
    component: () => import('@/pages/GuidePage.vue'),
    meta: { public: true, title: '辰科MES 使用指南' },
  },
  {
    path: '/trace',
    name: 'tracePublic',
    component: () => import('@/pages/TracePublicPage.vue'),
    meta: { public: true, title: '产品追溯信息' },
  },
  {
    path: '/report-unit',
    name: 'reportUnitRoot',
    component: () => import('@/pages/ReportUnitPage.vue'),
    meta: { title: '逐件报工' },
  },
  { path: '/t/:tenantCode/login', name: 'tenant-login', component: LoginPage, meta: { public: true, title: '登录' } },
  {
    path: '/t/:tenantCode',
    component: MainLayout,
    redirect: (to) => `/t/${String(to.params.tenantCode)}/home`,
    children: mainChildren,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

/** 客户账号不应误入的员工端页面 */
function isEmployeeOnlyH5Path(path: string): boolean {
  const p = stripTenantPrefix(path)
  if (p === '/home') return true
  if (p.startsWith('/tasks')) return true
  if (p === '/report' || p === '/report-unit' || p === '/report-manual' || p === '/report-history' || p === '/attendance' || p === '/wages') return true
  if (p.startsWith('/salary/')) return true
  return false
}

function loginPath(): string {
  const code = getStoredTenantCode()
  return code ? `/t/${code}/login` : '/login'
}

router.beforeEach(async (to) => {
  const fixedPath = fixDuplicateH5Path(to.path)
  if (fixedPath && fixedPath !== to.path) {
    return { path: fixedPath, query: to.query, hash: to.hash, replace: true }
  }

  const tenantFromQuery = to.query.tenant || to.query.tenant_code
  if (typeof tenantFromQuery === 'string' && tenantFromQuery.trim()) {
    setStoredTenantCode(tenantFromQuery.trim())
  }

  const code =
    parseTenantFromPath(to.path) ||
    (typeof to.params.tenantCode === 'string' ? to.params.tenantCode : null) ||
    (typeof tenantFromQuery === 'string' ? tenantFromQuery : null)
  if (code) setStoredTenantCode(code)

  const auth = useAuthStore()
  const token = auth.token
  const isPublic = Boolean(to.meta?.public)

  // 旧链接 /home、/tasks → 自动补上 /t/{租户编码}
  if (!isPublic && token && !parseTenantFromPath(to.path) && getStoredTenantCode()) {
    return { path: tenantH5Path(to.path), query: to.query, hash: to.hash, replace: true }
  }

  if (!isPublic && !token) {
    return { path: loginPath(), query: { redirect: to.fullPath } }
  }

  if (to.path === '/login' || /^\/t\/[^/]+\/login$/i.test(to.path)) {
    if (token) {
      if (!auth.userInfo) await auth.fetchMe()
      const tenantCode = code || getStoredTenantCode()
      if (auth.isCustomer) {
        return { name: 'customerOrder', params: { tenantCode }, replace: true }
      }
      const raw = (to.query.redirect as string) || '/home'
      return tenantH5Path(raw, tenantCode)
    }
    if (typeof document !== 'undefined') document.title = '登录'
    return true
  }

  if (!isPublic && token && !auth.userInfo) {
    await auth.fetchMe()
  }

  if (!isPublic && auth.userInfo && auth.isCustomer) {
    const sub = stripTenantPrefix(to.path)
    if (isEmployeeOnlyH5Path(to.path) || sub === '/home') {
      return { name: 'customerOrder', params: { tenantCode: code || getStoredTenantCode() }, replace: true }
    }
  }

  if (typeof document !== 'undefined') {
    const titleKey = to.meta?.titleKey as string | undefined
    document.title = titleKey ? i18n.global.t(titleKey) : ((to.meta?.title as string) || '辰科MES')
  }
  return true
})

router.onError((error) => {
  tryRecoverStaleChunk(error)
})

export default router
