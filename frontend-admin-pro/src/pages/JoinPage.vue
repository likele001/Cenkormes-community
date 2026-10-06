<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-[#fafafa]">
    <el-card class="w-full max-w-md">
      <template #header>{{ t('auth.register.joinEnterprise') }}</template>
      <el-form label-width="90px">
        <el-form-item :label="t('auth.register.username')"><el-input v-model="form.username" /></el-form-item>
        <el-form-item :label="t('auth.register.password')"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item :label="t('auth.register.fullName')"><el-input v-model="form.full_name" /></el-form-item>
        <LoginCaptchaField ref="captchaRef" />
        <el-button type="primary" class="w-full" :loading="loading" @click="submit">{{ t('auth.register.registerAndJoin') }}</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { http } from '@/utils/http'
import { redirectToH5Portal } from '@/utils/h5-entry'
import { parseTenantFromPath, setStoredTenantCode } from '@/utils/tenant'
import LoginCaptchaField from '@/components/LoginCaptchaField.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const loading = ref(false)
const captchaRef = ref<InstanceType<typeof LoginCaptchaField> | null>(null)
const form = reactive({ username: '', password: '', full_name: '' })
const token = ref('')

onMounted(() => {
  token.value = (route.query.invite as string) || ''
  const code = parseTenantFromPath(route.path) || (route.params.tenantCode as string)
  if (code) setStoredTenantCode(code)
})

async function submit() {
  if (!token.value) {
    ElMessage.warning(t('auth.register.invalidInvite'))
    return
  }
  const cap = captchaRef.value
  if (cap && !cap.validate()) {
    ElMessage.warning(t('auth.register.pleaseEnterCaptcha'))
    return
  }
  loading.value = true
  try {
    const res = await http.request<{ tenant_code: string }>({
      url: '/auth/register-by-invite',
      method: 'POST',
      data: { token: token.value, ...form, ...(cap?.payloadFields() || {}) },
    })
    ElMessage.success(t('auth.register.registerSuccess'))
    const code = res.tenant_code || (route.params.tenantCode as string) || ''
    if (!(await redirectToH5Portal(code, 'employee'))) {
      ElMessage.warning(t('auth.register.h5NotConfigured'))
    }
  } catch {
    await captchaRef.value?.refresh()
  } finally {
    loading.value = false
  }
}
</script>
