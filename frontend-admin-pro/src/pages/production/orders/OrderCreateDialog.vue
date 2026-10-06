<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('production.orders.createTitle')"
    width="720px"
    destroy-on-close
    @update:model-value="$emit('update:modelValue', $event)"
    @opened="loadOptions"
  >
    <div class="mb-3 flex items-center justify-between">
      <div class="text-sm text-zinc-500">一句话描述客户、型号与数量，AI 自动回填</div>
      <el-button type="primary" size="small" plain :loading="voiceLoading" @click="openVoice">
        <el-icon class="mr-1"><Mic /></el-icon>语音建单
      </el-button>
    </div>
    <div v-loading="optionsLoading">
      <el-form label-width="96px">
        <el-form-item :label="t('production.orders.customerLabel')" required>
          <el-select v-model="form.customer_id" filterable @change="onCustomerChange" :placeholder="t('production.orders.customerPlaceholder')" style="width: 100%">
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="partyOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="customerSummary" label=" " label-width="0">
          <div class="w-full rounded border border-blue-100 bg-blue-50/60 px-3 py-2 text-xs text-zinc-600">
            <div class="mb-1 flex items-center gap-2 font-medium text-blue-700">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ customerSummary.name }}（{{ customerSummary.code }}）</span>
            </div>
            <div class="grid grid-cols-2 gap-x-4 gap-y-0.5">
              <div v-if="customerSummary.contact_name || customerSummary.contact_phone">
                联系人：{{ customerSummary.contact_name || '-' }}{{ customerSummary.contact_phone ? ' · ' + customerSummary.contact_phone : '' }}
              </div>
              <div v-if="customerSummary.address">地址：{{ customerSummary.address }}</div>
              <div v-if="customerSummary.industry">行业：{{ customerSummary.industry }}</div>
              <div v-if="customerSummary.customer_level">等级：{{ customerSummary.customer_level }}</div>
            </div>
          </div>
        </el-form-item>
        <el-form-item :label="t('production.orders.code')">
          <el-input
            v-model="form.code"
            :placeholder="t('production.orders.orderCodePlaceholder')"
            maxlength="64"
            show-word-limit
          />
          <div class="text-xs text-zinc-500 mt-1">编号按日递增（ORD+日期+序号）。保存后会占用序号，下次自动为 002、003…</div>
        </el-form-item>
        <el-form-item :label="t('production.orders.dueDate')">
          <el-date-picker
            v-model="form.due_date"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="t('production.orders.remarkPlaceholder')"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('production.common.remark')">
          <el-input v-model="form.remark" type="textarea" :rows="2" :placeholder="t('production.orders.remarkPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('production.orders.productSku')" required>
          <div class="mb-2">
            <el-button size="small" @click="addLine">{{ t('production.orders.addSkuRow') }}</el-button>
          </div>
          <el-table class="w-full" :data="lines" border size="small">
            <el-table-column label="#" width="50">
              <template #default="{ $index }">{{ $index + 1 }}</template>
            </el-table-column>
            <el-table-column :label="t('production.orders.productSku')" min-width="280">
              <template #default="{ row }">
                <el-select
                  v-model="row.sku_id"
                  filterable
                  :placeholder="t('production.orders.skuPlaceholder')"
                  style="width: 100%"
                >
                  <el-option v-for="s in skus" :key="s.id" :label="orderSkuOptionLabel(s)" :value="s.id">
                    <div class="leading-tight py-0.5">
                      <div>{{ orderSkuOptionLabel(s) }}</div>
                      <div class="text-xs text-zinc-400">编码 {{ s.code }}</div>
                    </div>
                  </el-option>
                </el-select>
              </template>
            </el-table-column>
            <el-table-column :label="t('production.orders.quantityLabelCol')" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.qty" :min="1" :controls="false" class="!w-full" />
              </template>
            </el-table-column>
            <el-table-column :label="t('production.orders.rowRemarkLabel')" width="120">
              <template #default="{ row }">
                <el-input v-model="row.remark" :placeholder="t('production.orders.remarkPlaceholder')" />
              </template>
            </el-table-column>
            <el-table-column label="" width="70" fixed="right">
              <template #default="{ $index }">
                <el-button size="small" type="danger" link :disabled="lines.length <= 1" @click="removeLine($index)">删</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">{{ t('production.common.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ t('production.orders.saveDraft') }}</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="voiceOpen"
    title="语音建单"
    width="560px"
    align-center
    append-to-body
  >
    <div class="text-sm text-zinc-500 mb-2">描述客户、型号与数量，例如：「给北京宏达下 50 个标准件 A 款，周三交货」。AI 会提取并回填下方的订单草稿。</div>
    <el-input
      v-model="voiceText"
      type="textarea"
      :rows="4"
      :placeholder="'示例：给宏达电子下单 50 个标准件，备注加急，周三交货'"
      maxlength="1000"
      show-word-limit
    />
    <template #footer>
      <el-button @click="voiceOpen = false">取消</el-button>
      <el-button type="primary" :loading="voiceLoading" @click="applyVoiceDraft">解析并回填</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Mic, InfoFilled } from '@element-plus/icons-vue'
import { productionApi, type CustomerOut } from '@/api/production'
import { systemApi } from '@/api/system'
import { aiApi, type CustomerSuggestOut } from '@/api/ai'
import { codeForSubmit } from '@/utils/code'
import { orderSkuOptionLabel, partyOptionLabel, type OrderSkuOption } from '@/utils/display'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'created': []
}>()

const { t } = useI18n()
const optionsLoading = ref(false)
const saving = ref(false)
const customers = ref<CustomerOut[]>([])
const skus = ref<OrderSkuOption[]>([])

const form = reactive({
  customer_id: null as number | null,
  code: '',
  due_date: '' as string,
  remark: '',
})

const lines = reactive<{ sku_id: number | null; qty: number; remark: string }[]>([])

const voiceOpen = ref(false)
const voiceText = ref('')
const voiceLoading = ref(false)
const customerSummary = ref<CustomerSuggestOut | null>(null)

async function onCustomerChange(customerId: number | null) {
  customerSummary.value = null
  if (!customerId) return
  try {
    customerSummary.value = await aiApi.customerSuggest(customerId)
  } catch {
    customerSummary.value = null
  }
}

function openVoice() {
  voiceText.value = ''
  voiceOpen.value = true
}

async function applyVoiceDraft() {
  const text = voiceText.value.trim()
  if (!text) {
    ElMessage.warning('请先输入一句话描述')
    return
  }
  voiceLoading.value = true
  try {
    const draft = await aiApi.voiceOrderParse(text)
    // 回填客户
    if (draft.customer && customers.value.some((c) => c.id === draft.customer!.id)) {
      form.customer_id = draft.customer!.id
      await onCustomerChange(draft.customer!.id)
    } else if (draft.customer_hint && !draft.customer) {
      const hint = (draft.customer_hint || '').trim()
      const hit = customers.value.find(
        (c) => c.name === hint || c.code === hint || (hint && (c.name || '').includes(hint)),
      )
      if (hit) {
        form.customer_id = hit.id
        await onCustomerChange(hit.id)
      }
    }
    // 回填明细
    if ((draft.items || []).length) {
      lines.splice(
        0,
        lines.length,
        ...draft.items.map((it) => ({ sku_id: it.sku_id, qty: it.qty, remark: '' })),
      )
    }
    // 回填交期 / 备注
    if (draft.due_date) form.due_date = draft.due_date
    if (draft.remark) form.remark = draft.remark

    if (draft.customer) {
      ElMessage.success('已解析，请在下方确认后保存')
      voiceOpen.value = false
    } else {
      const un = (draft.unmatched || []).map((u) => `${u.name_hint}×${u.qty}`).join('、')
      ElMessage.warning(
        `未能完全识别客户，请手动选择客户。${un ? '未匹配到型号：' + un : ''}`,
      )
    }
  } finally {
    voiceLoading.value = false
  }
}

async function suggestedOrderCode() {
  try {
    const res = await systemApi.nextCode('order')
    return res.code
  } catch {
    return ''
  }
}

async function loadOptions() {
  optionsLoading.value = true
  try {
    const res = await productionApi.fetchOrderFormOptions()
    customers.value = (res.customers || []) as CustomerOut[]
    skus.value = res.skus || []
    if (!form.code.trim()) form.code = await suggestedOrderCode()
  } finally {
    optionsLoading.value = false
  }
}

/** Called by parent to initialize form state before opening */
async function resetForm() {
  form.customer_id = null
  form.code = await suggestedOrderCode()
  form.due_date = ''
  form.remark = ''
  lines.splice(0, lines.length, { sku_id: null, qty: 1, remark: '' })
}

function addLine() {
  lines.push({ sku_id: null, qty: 1, remark: '' })
}

function removeLine(idx: number) {
  if (lines.length <= 1) return
  lines.splice(idx, 1)
}

async function submit() {
  if (!form.customer_id) {
    ElMessage.warning('请选择客户')
    return
  }
  const rows = lines
    .filter((row) => row.sku_id != null && Number.isFinite(Number(row.qty)))
    .map((row, idx) => {
      const q = Math.max(1, Math.floor(Number(row.qty)))
      return {
        line_no: idx + 1,
        sku_id: row.sku_id as number,
        qty: q,
        remark: row.remark?.trim() ? row.remark.trim() : undefined,
      }
    })
  if (!rows.length) {
    ElMessage.warning('请至少填写一行型号与数量')
    return
  }
  saving.value = true
  try {
    await productionApi.createOrder({
      customer_id: form.customer_id as number,
      code: codeForSubmit(form.code) || undefined,
      due_date: form.due_date || undefined,
      remark: form.remark?.trim() || undefined,
      items: rows,
    })
    ElMessage.success('订单已创建（草稿）')
    emit('update:modelValue', false)
    emit('created')
  } finally {
    saving.value = false
  }
}

defineExpose({ resetForm })
</script>
