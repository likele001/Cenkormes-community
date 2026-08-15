<template>
  <AdminPage :title="t('system.wechatMp.title')">
    <template #actions>
      <el-button :loading="testing" @click="onTestConnection">
        {{ t('system.wechatMp.testConnection') }}
      </el-button>
      <el-button type="primary" :loading="saving" @click="save">
        {{ t('common.save') }}
      </el-button>
    </template>

    <el-card v-loading="loading" class="mb-4">
      <el-alert
        type="info"
        :closable="false"
        :title="t('system.wechatMp.howToUse')"
      >
        <ol class="text-sm list-decimal pl-5 space-y-1">
          <li>登录微信公众平台 → 开发管理 → 开发设置 → 获取 AppID 与 AppSecret</li>
          <li>登录微信公众平台 → 订阅消息 → 申请模板（每个事件需独立模板）</li>
          <li>把 AppID、AppSecret 填到下方，把模板 ID 填到对应事件</li>
          <li>保存后点击"测试连接"验证 AppSecret 是否正确</li>
        </ol>
      </el-alert>
    </el-card>

    <el-card :title="t('system.wechatMp.basicSettings')" class="mb-4">
      <el-form label-width="160px" class="max-w-2xl">
        <el-form-item :label="t('system.wechatMp.enabled')">
          <el-switch v-model="form.enabled" />
          <span class="ml-2 text-xs text-zinc-500">
            {{ form.enabled ? t('system.wechatMp.enabledOn') : t('system.wechatMp.enabledOff') }}
          </span>
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.appid')">
          <el-input
            v-model="form.appid"
            placeholder="wx..."
            maxlength="64"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.appSecret')">
          <el-input
            v-model="form.app_secret"
            :placeholder="
              form.app_secret_masked
                ? t('system.wechatMp.appSecretKeepHint') + '（' + form.app_secret_masked + '）'
                : t('system.wechatMp.appSecretHint')
            "
            maxlength="128"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.miniprogramState')">
          <el-radio-group v-model="form.miniprogram_state">
            <el-radio-button value="formal">formal（线上版）</el-radio-button>
            <el-radio-button value="trial">trial（体验版）</el-radio-button>
            <el-radio-button value="developer">developer（开发版）</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.defaultPage')">
          <el-input
            v-model="form.default_page"
            placeholder="pages-employee/dashboard/index"
            maxlength="255"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card :title="t('system.wechatMp.eventRules')" class="mb-4">
      <el-table :data="ruleRows" stripe size="small">
        <el-table-column :label="t('system.wechatMp.event')" min-width="180">
          <template #default="{ row }">
            <div class="font-medium">{{ row.label }}</div>
            <div class="text-xs text-zinc-500">{{ row.code }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="t('system.wechatMp.eventEnabled')" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.rule.enabled" />
          </template>
        </el-table-column>
        <el-table-column :label="t('system.wechatMp.templateId')" min-width="200">
          <template #default="{ row }">
            <el-input
              v-model="row.rule.template_id"
              :placeholder="t('system.wechatMp.templateIdHint')"
              size="small"
              maxlength="128"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('system.wechatMp.page')" min-width="200">
          <template #default="{ row }">
            <el-input
              v-model="row.rule.page"
              :placeholder="t('system.wechatMp.pageHint')"
              size="small"
              maxlength="255"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('system.wechatMp.keywordHint')" min-width="240">
          <template #default="{ row }">
            <div class="text-xs text-zinc-500 leading-relaxed">
              <template v-if="row.hint && row.hint.length">
                <div v-for="(kw, i) in row.hint" :key="i">
                  keyword{{ i + 1 }}: {{ kw }}
                </div>
              </template>
              <span v-else class="text-zinc-400">—</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card :title="t('system.wechatMp.testSend')" class="mb-4">
      <el-form label-width="100px" class="max-w-xl" inline>
        <el-form-item :label="t('system.wechatMp.testOpenid')">
          <el-input v-model="test.openid" placeholder="用户的 openid" style="width: 240px" />
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.testTemplateId')">
          <el-input v-model="test.template_id" placeholder="已配置的 template_id" style="width: 220px" />
        </el-form-item>
        <el-form-item :label="t('system.wechatMp.testPage')">
          <el-input v-model="test.page" placeholder="pages-employee/dashboard/index" style="width: 220px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="testSending" @click="onTestSend">
            {{ t('system.wechatMp.sendTest') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card :title="t('system.wechatMp.pushLogs')">
      <AdminDataTable
        :loading="logsLoading"
        :empty="!logs.length"
        :total="logsTotal"
        :current-page="logsPage"
        :page-size="20"
        @page-change="(p) => { logsPage = p; loadLogs() }"
      >
        <template #table>
          <el-table :data="logs" stripe size="small">
            <el-table-column prop="id" :label="t('system.wechatMp.logId')" width="70" />
            <el-table-column prop="event_code" :label="t('system.wechatMp.event')" min-width="160" />
            <el-table-column :label="t('system.wechatMp.openid')" width="180">
              <template #default="{ row }">
                <span class="text-xs font-mono">{{ row.openid }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="template_id" :label="t('system.wechatMp.templateId')" width="160" />
            <el-table-column prop="title" :label="t('system.wechatMp.title2')" min-width="160" show-overflow-tooltip />
            <el-table-column :label="t('system.wechatMp.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('system.wechatMp.error')" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.error_msg" class="text-xs text-red-600">{{ row.error_msg }}</span>
                <span v-else class="text-zinc-400">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" :label="t('system.wechatMp.createdAt')" width="170" />
            <el-table-column :label="t('common.operation')" width="80" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'failed'" size="small" link @click="onRetry(row)">
                  {{ t('common.retry') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </AdminDataTable>
    </el-card>
  </AdminPage>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminPage from '@/components/admin/AdminPage.vue'
import AdminDataTable from '@/components/admin/AdminDataTable.vue'
import { wechatMpApi, WECHAT_MP_EVENT_LABELS, type WechatMpSettings, type WechatMpPushLog } from '@/api/wechatMp'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const testSending = ref(false)

const form = ref({
  enabled: false,
  appid: '',
  app_secret: '',
  app_secret_masked: '',
  miniprogram_state: 'formal' as 'formal' | 'trial' | 'developer',
  default_page: 'pages-employee/dashboard/index',
})

const ruleRows = ref<{ code: string; label: string; rule: { enabled: boolean; template_id: string; page: string; targets?: string[] }; hint: string[] }[]>([])

const test = ref({ openid: '', template_id: '', page: '' })

const logsLoading = ref(false)
const logs = ref<WechatMpPushLog[]>([])
const logsTotal = ref(0)
const logsPage = ref(1)

const statusType = (s: string) => {
  if (s === 'sent') return 'success'
  if (s === 'failed') return 'danger'
  if (s === 'pending') return 'info'
  return 'info'
}
const statusLabel = (s: string) => {
  if (s === 'sent') return t('system.wechatMp.statusSent')
  if (s === 'failed') return t('system.wechatMp.statusFailed')
  if (s === 'pending') return t('system.wechatMp.statusPending')
  return s
}

async function loadAll() {
  loading.value = true
  try {
    const cfg = await wechatMpApi.getSettings()
    form.value = {
      enabled: !!cfg.enabled,
      appid: cfg.appid || '',
      app_secret: '',   // 后端不返回明文
      app_secret_masked: cfg.app_secret_masked || '',
      miniprogram_state: (cfg.miniprogram_state || 'formal') as any,
      default_page: cfg.default_page || 'pages-employee/dashboard/index',
    }
    ruleRows.value = Object.keys(WECHAT_MP_EVENT_LABELS).map((code) => ({
      code,
      label: WECHAT_MP_EVENT_LABELS[code] || code,
      rule: cfg.rules?.[code] || { enabled: true, template_id: '', page: '', targets: [] },
      hint: cfg.keyword_hints?.[code] || [],
    }))
  } finally {
    loading.value = false
  }
  await loadLogs()
}

async function save() {
  saving.value = true
  try {
    const rulesPayload: Record<string, any> = {}
    for (const r of ruleRows.value) {
      rulesPayload[r.code] = {
        enabled: r.rule.enabled,
        template_id: r.rule.template_id?.trim() || '',
        page: r.rule.page?.trim() || '',
        targets: r.rule.targets || [],
      }
    }
    await wechatMpApi.saveSettings({
      enabled: form.value.enabled,
      appid: form.value.appid.trim(),
      app_secret: form.value.app_secret.trim(),  // 空串 = 后端保留旧值
      miniprogram_state: form.value.miniprogram_state,
      default_page: form.value.default_page.trim(),
      rules: rulesPayload,
    } as any)
    ElMessage.success(t('system.wechatMp.saveSuccess'))
    await loadAll()
  } finally {
    saving.value = false
  }
}

async function onTestConnection() {
  testing.value = true
  try {
    const r = await wechatMpApi.testConnection()
    ElMessage.success(t('system.wechatMp.testOk') + (r.token_preview ? ` (token: ${r.token_preview}...)` : ''))
  } catch (e: any) {
    ElMessage.error(t('system.wechatMp.testFailed') + ': ' + (e?.detail || e?.message || ''))
  } finally {
    testing.value = false
  }
}

async function onTestSend() {
  if (!test.value.openid || !test.value.template_id) {
    ElMessage.warning(t('system.wechatMp.testFieldsRequired'))
    return
  }
  testSending.value = true
  try {
    const r = await wechatMpApi.testSend({
      openid: test.value.openid,
      template_id: test.value.template_id,
      title: 'LightMes 测试推送',
      content: '这是一条来自管理后台的测试消息，验证你的模板配置是否正确。',
      page: test.value.page || form.value.default_page,
    })
    ElMessage.success(t('system.wechatMp.testSendOk') + (r.message_id ? ` (msgid: ${r.message_id})` : ''))
    loadLogs()
  } catch (e: any) {
    ElMessage.error(t('system.wechatMp.testSendFailed') + ': ' + (e?.detail || e?.message || ''))
  } finally {
    testSending.value = false
  }
}

async function loadLogs() {
  logsLoading.value = true
  try {
    const r = await wechatMpApi.listPushLogs({ offset: (logsPage.value - 1) * 20, limit: 20 })
    logs.value = r.items || []
    logsTotal.value = logs.value.length  // 简单近似
  } finally {
    logsLoading.value = false
  }
}

async function onRetry(row: WechatMpPushLog) {
  try {
    await ElMessageBox.confirm(t('system.wechatMp.retryConfirm'), t('common.confirm'), { type: 'info' })
  } catch {
    return
  }
  try {
    await wechatMpApi.retryPushLog(row.id)
    ElMessage.success(t('system.wechatMp.retryQueued'))
    loadLogs()
  } catch (e: any) {
    ElMessage.error(t('system.wechatMp.retryFailed') + ': ' + (e?.detail || e?.message || ''))
  }
}

onMounted(loadAll)
</script>
