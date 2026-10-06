<template>
  <div class="admin-login-page min-h-screen w-screen flex items-center justify-center p-4">
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-60" aria-hidden="true">
      <div class="absolute -top-24 -right-24 w-72 h-72 rounded-full admin-login-blob-primary" />
      <div class="absolute -bottom-20 -left-16 w-64 h-64 rounded-full admin-login-blob-secondary" />
    </div>

    <div
      class="admin-login-card relative w-full max-w-[420px] rounded-lg border p-8 sm:p-9 shadow-[var(--el-box-shadow)] admin-interactive"
    >
      <AdminBrand :subtitle="t('auth.login.enterpriseAdmin')" :use-tenant="false" class="mb-1" />
      <p class="text-[13px] text-[var(--admin-brand-subtitle)] mt-4 mb-5">{{ t('auth.login.hint') }}</p>
      <p v-if="employeeH5Url" class="text-xs mb-4" style="color: var(--el-color-primary)">
        <a :href="employeeH5Url" target="_blank" rel="noopener">{{ t('auth.login.employeeEntry') }}</a>
      </p>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="login-form">
        <el-form-item :label="t('auth.login.tenantCode')" prop="tenant_code">
          <el-input v-model="form.tenant_code" autocomplete="off" />
        </el-form-item>
        <el-form-item :label="t('auth.login.username')" prop="username">
          <el-input v-model="form.username" autocomplete="off" />
        </el-form-item>
        <el-form-item :label="t('auth.login.password')" prop="password">
          <el-input v-model="form.password" type="password" show-password autocomplete="off" />
        </el-form-item>
        <LoginCaptchaField ref="captchaRef" />
        <el-form-item class="!mb-2">
          <el-checkbox v-model="rememberMe">{{ t('auth.login.rememberMe') }}</el-checkbox>
          <p class="text-xs text-el-placeholder mt-1 w-full">{{ t('auth.login.rememberMeDesc') }}</p>
        </el-form-item>
        <el-form-item class="!mb-0 mt-1">
          <el-button class="w-full" type="primary" :loading="loading" @click="onSubmit">{{ t('auth.login.loginBtn') }}</el-button>
        </el-form-item>
        <p v-if="registerEnabled" class="text-center text-sm mt-3">
          <a :href="portalUrl" style="color: var(--el-color-primary)">{{ t('auth.login.registerNew') }}</a>
        </p>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { buildH5Url, redirectToH5Portal } from '@/utils/h5-entry'
import {
  getStoredTenantCode,
  parseTenantFromPath,
  resolvePostLoginPath,
  setStoredTenantCode,
} from '@/utils/tenant'
import { platformApi } from '@/api/platform'
import LoginCaptchaField from '@/components/LoginCaptchaField.vue'
import AdminBrand from '@/components/AdminBrand.vue'
import { loadRememberPreference, saveRememberPreference } from '@/utils/session-token'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { t } = useI18n()

const formRef = ref<FormInstance>()
const loading = ref(false)
const registerEnabled = ref(false)
const employeeH5Url = ref('')
const portalUrl = ref('')
const captchaRef = ref<InstanceType<typeof LoginCaptchaField> | null>(null)
const rememberMe = ref(loadRememberPreference())
const form = reactive({ tenant_code: '', username: '', password: '' })

async function refreshEmployeeH5Link() {
  const tc = form.tenant_code.trim()
  if (!tc) {
    employeeH5Url.value = ''
    return
  }
  employeeH5Url.value = (await buildH5Url(tc, `/t/${tc.toUpperCase()}/login`)) || ''
}

onMounted(async () => {
  const fromPath = parseTenantFromPath(route.path) || (route.params.tenantCode as string) || getStoredTenantCode()
  if (fromPath) {
    form.tenant_code = fromPath
    setStoredTenantCode(fromPath)
  }
  try {
    const cfg = await platformApi.publicConfig()
    registerEnabled.value = cfg.register_enabled
    // 优先用后端返回的 portal_site_url；后端未配置时按当前 host 推导 portal 子域，避免击回 /register
    portalUrl.value = computePortalUrl(cfg.portal_site_url)
  } catch {
    registerEnabled.value = false
    // 接口异常时也走本地推导，保持可用性
    portalUrl.value = computePortalUrl('')
  }
  await refreshEmployeeH5Link()
})

/**
 * 计算注册入口 URL。
 * 1. 优先用后端返回的 portal_site_url + '/register'
 * 2. 若后端未配置，从当前 host 推导：admin.mes.cenkor.cn -> https://portal.mes.cenkor.cn
 * 3. 最后走 import.meta.env.VITE_PORTAL_URL 静态兑底
 */
function computePortalUrl(raw: string | undefined | null): string {
  const trimmed = (raw || '').trim().replace(/\/$/, '')
  if (trimmed) return trimmed + '/register'
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location
    // 从当前 host 推导 portal 子域：admin.mes.cenkor.cn -> portal.mes.cenkor.cn
    const derivedHost = hostname.replace(/^admin\./, 'portal.')
    return `${protocol}//${derivedHost}/register`
  }
  // SSR / 环境变量兜底
  const fallback = ((import.meta.env.VITE_PORTAL_URL as string | undefined) || '').trim().replace(/\/$/, '') || 'https://portal.mes.cenkor.cn'
  return fallback + '/register'
}

watch(() => form.tenant_code, () => {
  void refreshEmployeeH5Link()
})

const rules: FormRules = {
  tenant_code: [{ required: true, message: t('auth.login.pleaseEnterTenantCode'), trigger: 'blur' }],
  username: [{ required: true, message: t('auth.login.pleaseEnterUsername'), trigger: 'blur' }],
  password: [{ required: true, message: t('auth.login.pleaseEnterPassword'), trigger: 'blur' }],
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  loading.value = true
  try {
    const cap = captchaRef.value
    if (cap && !cap.validate()) {
      ElMessage.warning(t('auth.login.pleaseEnterCaptcha'))
      return
    }
    saveRememberPreference(rememberMe.value)
    const tenantCode = form.tenant_code.trim().toUpperCase()
    setStoredTenantCode(tenantCode)
    await auth.login({ ...form, tenant_code: tenantCode, remember_me: rememberMe.value, ...(cap?.payloadFields() || {}) })
    const redirect =
      typeof route.query.redirect === 'string' ? route.query.redirect : null
    await router.replace(resolvePostLoginPath(tenantCode, redirect))
  } catch (e: unknown) {
    await captchaRef.value?.refresh()
    const msg = e instanceof Error ? e.message : t('auth.login.loginFailed')
    if (msg.includes('H5')) {
      const tc = form.tenant_code.trim()
      const kind = msg.includes('客户') ? 'customer' : 'employee'
      if (tc && (await redirectToH5Portal(tc, kind))) return
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--el-text-color-regular);
}
</style>
