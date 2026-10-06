<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { closeToast, showDialog, showLoadingToast, showToast } from 'vant'
import { uploadFile } from '@/api/files'
import { photoAiCount, defectAiClassify, attachmentIdToUrl } from '@/api/ai'
import {
  createTempReport,
  getTempReportOptions,
  listMyTempReports,
  type TempReport,
  type TempReportOptionsOut,
} from '@/api/tempReports'

type PickerKind = 'products' | 'skus' | 'processes'

const submitting = ref(false)
const aiCounting = ref(false)
const aiClassifying = ref(false)
const options = ref<TempReportOptionsOut | null>(null)
const list = ref<TempReport[]>([])

const productId = ref<number | null>(null)
const skuId = ref<number | null>(null)
const processId = ref<number | null>(null)
const goodQty = ref<string>('')
const badQty = ref<string>('')
const remark = ref('')
const uploads = ref<{ id: number; name: string }[]>([])
const attachmentIds = ref('')

// Picker 弹层状态
const showPicker = ref(false)
const pickerKind = ref<PickerKind>('products')
const pickerTitle = computed(() =>
  pickerKind.value === 'products' ? '选择产品型号' : pickerKind.value === 'skus' ? '选择SKU' : '选择工序',
)

function optLabel(o: { code: string | null; name: string | null }): string {
  if (o.code && o.name) return `${o.code} - ${o.name}`
  return o.name || o.code || ''
}

function pickerColumns(): { text: string; value: number }[] {
  const col = options.value?.[pickerKind.value] || []
  return col.map((o) => ({ text: optLabel(o), value: o.id }))
}

function currentDisplay(kind: PickerKind): string {
  const id = kind === 'products' ? productId.value : kind === 'skus' ? skuId.value : processId.value
  const o = options.value?.[kind].find((x) => x.id === id)
  return o ? optLabel(o) : ''
}

function openPicker(kind: PickerKind) {
  if (!options.value || options.value[kind].length === 0) {
    showToast('暂无可选项目')
    return
  }
  pickerKind.value = kind
  showPicker.value = true
}

function onPickerConfirm(val: { value: number }) {
  if (pickerKind.value === 'products') productId.value = val.value
  else if (pickerKind.value === 'skus') skuId.value = val.value
  else processId.value = val.value
  showPicker.value = false
}

function productName(id: number | null) {
  return options.value?.products.find((p) => p.id === id)?.name ?? null
}
function processName(id: number | null) {
  return options.value?.processes.find((p) => p.id === id)?.name ?? null
}

async function refresh() {
  try {
    const res = await listMyTempReports()
    list.value = res.items || []
  } catch {
    list.value = []
  }
}

function handleUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.multiple = false
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    const toast = showLoadingToast({ message: '上传中...', duration: 0 })
    try {
      const resp = (await uploadFile(file)) as any
      const id = resp?.id ?? resp?.file_id
      if (id) {
        uploads.value.push({ id, name: file.name })
        attachmentIds.value = uploads.value.map((u) => u.id).join(',')
        showToast('上传成功')
      }
    } catch {
      showToast('上传失败')
    } finally {
      closeToast()
    }
  }
  input.click()
}

function removeUpload(idx: number) {
  uploads.value.splice(idx, 1)
  attachmentIds.value = uploads.value.map((u) => u.id).join(',')
}

async function handleAiCount() {
  if (uploads.value.length === 0) {
    showToast('请先上传照片')
    return
  }
  aiCounting.value = true
  try {
    const image_urls = uploads.value.map((u) => attachmentIdToUrl(u.id, u.name))
    const res = await photoAiCount({ image_urls })
    if (!res.ok) {
      showToast(res.error || 'AI 计数不可用')
      return
    }
    const cur = Number(res.count || 0)
    if (cur <= 0) {
      showToast('AI 未识别到零件')
      return
    }
    goodQty.value = String(cur)
    showDialog({ title: 'AI 计数完成', message: `识别 ${res.image_count} 张照片，共 ${cur} 件。${res.note || ''}`, confirmButtonText: '好的' })
  } catch (e) {
    showToast(e instanceof Error ? e.message : 'AI 计数失败')
  } finally {
    aiCounting.value = false
  }
}

async function handleAiClassify() {
  if (uploads.value.length === 0) {
    showToast('请先上传不良品照片')
    return
  }
  aiClassifying.value = true
  try {
    const image_urls = uploads.value.map((u) => attachmentIdToUrl(u.id, u.name))
    const res = await defectAiClassify({
      image_urls,
      remark: remark.value.trim() || undefined,
    })
    if (!res.ok) {
      showToast(res.error || 'AI 分类不可用')
      return
    }
    let msg = `识别 ${res.image_count} 张照片`
    if (res.defect_name) msg += `\n缺陷类型：${res.defect_name}`
    if (res.severity) msg += `\n严重程度：${res.severity}`
    if (res.description) msg += `\n说明：${res.description}`
    if (res.confidence) msg += `\n可信度：${res.confidence}`
    if (res.description && !remark.value.trim()) remark.value = res.description
    showDialog({ title: 'AI 缺陷分类', message: msg, confirmButtonText: '好的' })
  } catch (e) {
    showToast(e instanceof Error ? e.message : 'AI 分类失败')
  } finally {
    aiClassifying.value = false
  }
}

async function submit() {
  const good = Number(goodQty.value) || 0
  const bad = Number(badQty.value) || 0
  if (good + bad <= 0) {
    showToast('合格数+不良数必须大于0')
    return
  }
  submitting.value = true
  try {
    await createTempReport({
      product_id: productId.value,
      sku_id: skuId.value,
      process_id: processId.value,
      good_qty: good,
      bad_qty: bad,
      remark: remark.value || null,
      attachment_ids: attachmentIds.value || null,
    })
    showToast('临时报工已提交')
    goodQty.value = ''
    badQty.value = ''
    remark.value = ''
    uploads.value = []
    attachmentIds.value = ''
    refresh()
  } catch (e) {
    showToast(e instanceof Error ? e.message : '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    options.value = await getTempReportOptions()
  } catch {
    options.value = null
  }
  refresh()
})
</script>

<template>
  <div class="min-h-screen bg-zinc-100 pb-8">
    <div class="mx-4 mt-4 rounded-xl bg-white p-4 shadow-sm">
      <div class="text-base font-medium text-zinc-800">临时报工（无单自记录）</div>
      <div class="mt-1 text-xs text-zinc-500">适用于没有正式工单的临时活，提交后由管理员补绑到对应工单</div>

      <!-- 产品型号 -->
      <div class="mt-3">
        <div class="mb-1 text-sm text-zinc-600">产品型号</div>
        <van-field
          :readonly="true"
          :model-value="currentDisplay('products')"
          placeholder="点击选择（可留空）"
          :is-link="true"
          @click="openPicker('products')"
        />
      </div>

      <!-- 工序 -->
      <div class="mt-3">
        <div class="mb-1 text-sm text-zinc-600">工序</div>
        <van-field
          :readonly="true"
          :model-value="currentDisplay('processes')"
          placeholder="点击选择（可留空）"
          :is-link="true"
          @click="openPicker('processes')"
        />
      </div>

      <div class="mt-3 grid grid-cols-2 gap-3">
        <div>
          <div class="mb-1 text-sm text-zinc-600">合格数</div>
          <van-field v-model="goodQty" type="number" placeholder="合格数量" />
        </div>
        <div>
          <div class="mb-1 text-sm text-zinc-600">不良数</div>
          <van-field v-model="badQty" type="number" placeholder="不良数量" />
        </div>
      </div>

      <div class="mt-3">
        <div class="mb-1 text-sm text-zinc-600">备注</div>
        <van-field
          v-model="remark"
          type="textarea"
          rows="2"
          maxlength="500"
          placeholder="如：现场临时任务、补活、返工原因等，方便管理员正确关联"
        />
      </div>

      <!-- 拍照留底 -->
      <div class="mt-3">
        <div class="mb-1 text-sm text-zinc-600">现场照片（选填）</div>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(u, idx) in uploads"
            :key="u.id"
            class="relative h-16 w-16 overflow-hidden rounded-lg border border-zinc-200"
          >
            <div class="flex h-full w-full items-center justify-center bg-zinc-50 text-xs text-zinc-400">照片{{ idx + 1 }}</div>
            <div class="absolute right-0 top-0 cursor-pointer bg-black/50 px-1 text-white text-xs" @click="removeUpload(idx)">✕</div>
          </div>
          <div
            class="flex h-16 w-16 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-zinc-300 text-zinc-400"
            @click="handleUpload"
          >
            <div class="text-xl">＋</div>
            <div class="text-xs">拍照</div>
          </div>
        </div>
      </div>

      <!-- AI 辅助 -->
      <div v-if="uploads.length" class="mt-3 flex gap-2">
        <van-button
          size="small"
          type="warning"
          plain
          block
          :loading="aiCounting"
          @click="handleAiCount"
        >
          AI 拍照计数
        </van-button>
        <van-button
          size="small"
          type="danger"
          plain
          block
          :loading="aiClassifying"
          @click="handleAiClassify"
        >
          AI 缺陷分类
        </van-button>
      </div>

      <van-button block type="primary" :loading="submitting" class="mt-4" @click="submit">提交临时报工</van-button>
    </div>

    <!-- 我的临时报工记录 -->
    <div class="mx-4 mt-4 rounded-xl bg-white p-4 shadow-sm">
      <div class="mb-2 text-base font-medium text-zinc-800">我的临时报工</div>
      <div v-if="list.length === 0" class="py-6 text-center text-sm text-zinc-400">暂无记录</div>
      <div v-for="t in list" :key="t.id" class="border-b border-zinc-100 py-2 last:border-0">
        <div class="flex items-center justify-between text-sm">
          <span class="text-zinc-800">
            {{ productName(t.product_id) || t.product?.code || '未填产品' }}
            <span v-if="processName(t.process_id)"> / {{ processName(t.process_id) }}</span>
          </span>
          <span
            class="rounded px-1.5 py-0.5 text-xs"
            :class="t.status === 'bound' ? 'bg-green-100 text-green-600' : t.status === 'void' ? 'bg-zinc-100 text-zinc-500' : 'bg-amber-100 text-amber-600'"
          >
            {{ t.status === 'bound' ? '已关联' : t.status === 'void' ? '已作废' : '待关联' }}
          </span>
        </div>
        <div class="mt-0.5 text-xs text-zinc-500">
          合格 {{ t.good_qty }} / 不良 {{ t.bad_qty }}
          <span v-if="(t.remaining_qty ?? 0) < t.good_qty + t.bad_qty"> · 已并入 {{ t.qty_bound ?? 0 }}</span>
        </div>
        <div class="text-xs text-zinc-400">{{ t.created_at }}</div>
      </div>
    </div>

    <!-- 下拉选择器弹层 -->
    <van-popup v-model:show="showPicker" position="bottom" round>
      <van-picker
        :title="pickerTitle"
        :columns="pickerColumns()"
        @confirm="onPickerConfirm"
        @cancel="showPicker = false"
      />
    </van-popup>
  </div>
</template>