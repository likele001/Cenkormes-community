<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showConfirmDialog, showToast } from 'vant'
import {
  ackMyStatement,
  downloadMyStatementCsv,
  getMyStatementDetail,
  submitMyStatementPayment,
  type CustomerStatementDetail,
} from '@/api/customer'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const downloading = ref(false)
const actionLoading = ref(false)
const data = ref<CustomerStatementDetail | null>(null)
const paymentRemark = ref('')

const statementId = computed(() => Number(route.params.id))
const canAck = computed(() => data.value?.status === 'draft')
const canSubmitPayment = computed(() => data.value?.status === 'confirmed')
const hasSubmitted = computed(() => !!data.value?.payment_submitted_at)
const submitPaymentLabel = computed(() =>
  hasSubmitted.value
    ? t('customer.statementDetail.resubmitPayment')
    : t('customer.statementDetail.submitPayment'),
)

function periodLabel() {
  const s = data.value?.period_start || '—'
  const e = data.value?.period_end || '—'
  return `${s} ~ ${e}`
}

async function load() {
  const id = statementId.value
  if (!id) return
  loading.value = true
  try {
    data.value = await getMyStatementDetail(id)
  } finally {
    loading.value = false
  }
}

async function onAck() {
  const id = statementId.value
  if (!id || actionLoading.value) return
  try {
    await showConfirmDialog({ title: t('customer.statementDetail.confirmAck'), message: t('customer.statementDetail.confirmAckMessage') })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    await ackMyStatement(id)
    showToast(t('customer.statementDetail.ackSuccess'))
    await load()
  } finally {
    actionLoading.value = false
  }
}

async function onSubmitPayment() {
  const id = statementId.value
  if (!id || actionLoading.value) return
  try {
    await showConfirmDialog({ title: submitPaymentLabel.value, message: t('customer.statementDetail.confirmSubmitPayment') })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    await submitMyStatementPayment(id, paymentRemark.value.trim() || undefined)
    showToast(t('customer.statementDetail.submitPaymentSuccess'))
    paymentRemark.value = ''
    await load()
  } finally {
    actionLoading.value = false
  }
}

async function onDownload() {
  const id = statementId.value
  if (!id || downloading.value) return
  downloading.value = true
  try {
    const blob = await downloadMyStatementCsv(id)
    const name = `${data.value?.code || 'statement'}.csv`
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch {
    showToast(t('customer.statementDetail.downloadFailed'))
  } finally {
    downloading.value = false
  }
}

watch(statementId, load, { immediate: true })
</script>

<template>
  <div>
    <div class="mt-2">
      <van-loading v-if="loading" class="mx-auto" />
    </div>

    <template v-if="data">
      <van-cell-group inset>
        <van-cell :title="t('customer.statementDetail.statementNo')" :value="data.code" />
        <van-cell :title="t('customer.statementDetail.period')" :value="periodLabel()" />
        <van-cell :title="t('customer.statementDetail.status')" :value="data.status || '—'" />
        <van-cell :title="t('customer.statementDetail.totalAmount')" :value="`¥${data.total_amount}`" />
        <van-cell :title="t('customer.statementDetail.remark')" :value="data.remark || '—'" />
      </van-cell-group>

      <div class="mt-4 px-4">
        <van-button block type="primary" :loading="actionLoading" :disabled="!canAck" @click="onAck">{{ t('customer.statementDetail.confirmAck') }}</van-button>
      </div>

      <div v-if="hasSubmitted" class="mt-3 px-4">
        <div class="rounded-lg bg-amber-50 px-3 py-2 text-[13px] leading-5 text-amber-700">
          {{ t('customer.statementDetail.paymentSubmittedTip') }}{{ data.payment_submitted_at ? `（${data.payment_submitted_at}）` : '' }}
          <div v-if="data.payment_submitted_remark" class="mt-1 text-amber-600">
            {{ t('customer.statementDetail.paymentRemark') }}：{{ data.payment_submitted_remark }}
          </div>
        </div>
      </div>

      <div v-if="canSubmitPayment" class="mt-3 px-4">
        <van-field
          v-model="paymentRemark"
          :placeholder="t('customer.statementDetail.paymentRemarkPlaceholder')"
          maxlength="255"
          class="rounded-lg"
        />
      </div>

      <div class="mt-3 px-4">
        <van-button block type="warning" :loading="actionLoading" :disabled="!canSubmitPayment" @click="onSubmitPayment">
          {{ submitPaymentLabel }}
        </van-button>
      </div>

      <div class="mt-4 px-3 text-[14px] font-semibold text-zinc-700">{{ t('customer.statementDetail.detail') }}</div>
      <van-cell-group inset class="mt-2">
        <van-cell v-for="it in data.items" :key="it.order_id" :title="it.order_code || `订单#${it.order_id}`" :value="`¥${it.amount}`" />
      </van-cell-group>

      <div class="mt-6 px-4">
        <van-button block type="primary" :loading="downloading" @click="onDownload">{{ t('customer.statementDetail.downloadCsv') }}</van-button>
      </div>

      <div class="mt-3 px-4">
        <van-button block @click="router.push({ name: 'customerStatements' })">{{ t('customer.statementDetail.returnList') }}</van-button>
      </div>
    </template>
  </div>
</template>
