import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { LoginIn, MeOut } from '@/api/auth'
import { loginApi, meApi } from '@/api/auth'
import { clearStoredTenantCode, setStoredTenantCode } from '@/utils/tenant'
import { clearToken, getToken, setToken } from '@/utils/token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getToken()) // 支持 local / session 存储
  const me = ref<MeOut | null>(null)
  const permissions = computed(() => me.value?.permissions ?? [])
  const blockedModules = computed(() => me.value?.blockedModules ?? [])
  const isTrial = computed(() => blockedModules.value.length > 0)

  // 试用基础版隐藏的顶层/子菜单路径前缀（与后端 blocked_modules 对应）
  const TRIAL_BLOCKED_PATHS = [
    '/ai', '/finance', '/erp', '/purchase', '/warehouse', '/crm',
    '/production/equipment', '/production/trace', '/production/shifts',
    '/system/feishu-notify', '/system/wecom-notify', '/system/dingtalk-notify',
    '/system/message-center', '/system/push-monitor', '/system/print-templates',
    '/system/skills', '/system/attendance-records', '/system/operation-logs',
    '/system/industry-packs', '/system/approval-flows',
  ]

  function isPathBlocked(path: string): boolean {
    if (!isTrial.value || !path) return false
    return TRIAL_BLOCKED_PATHS.some((p) => path === p || path.startsWith(p + '/'))
  }

  function hasAnyPermission(codes?: string[] | string): boolean {
    if (!codes) return true
    const need = Array.isArray(codes) ? codes : [codes]
    if (need.length === 0) return true
    const set = new Set(permissions.value)
    return need.some((x) => set.has(x))
  }

  async function login(payload: LoginIn) {
    const res = await loginApi(payload)
    token.value = res.access_token
    setToken(res.access_token, Boolean(payload.remember_me))
    await fetchMe()
    if (me.value?.tenant_code) setStoredTenantCode(me.value.tenant_code)
  }

  async function fetchMe() {
    const data = await meApi()
    me.value = data
  }

  function logout() {
    token.value = null
    me.value = null
    clearToken()
    clearStoredTenantCode()
  }

  return { token, me, permissions, blockedModules, isTrial, isPathBlocked, hasAnyPermission, login, fetchMe, logout }
})

