<script setup lang="ts">
/**
 * NewUserGuide · 新用户首次登录引导 + 全局"重新引导"事件监听
 * 自绘全屏遮罩 + 中央卡片，驱动式，生产链路 4 步引导。
 *
 * 自动：首次登录自动弹出一次；完成/跳过即写 localStorage。
 * 手动：任何地方 dispatchEvent(new CustomEvent('cenkormes:reopen-guide'))
 *       即重开引导（用于帮助页"重新引导"按钮）。组件内同时暴露 openNow()。
 */
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tenantAdminPath } from '@/utils/tenant'

const GUIDE_KEY = 'cenkormes_guide_done_v1'
const REOPEN_EVENT = 'cenkormes:reopen-guide'

const props = defineProps<{
  autoShow?: boolean
}>()

const router = useRouter()
const auth = useAuthStore()

const show = ref(false)
const current = ref(0)

const steps = [
  {
    title: '欢迎使用 CenkorMES',
    desc: '这是一条贯穿「建产品 → 建订单 → 下达工单 → 派工 → 扫码报工」的核心制造链路。下面 4 步带你快速上手，可随时点「跳过」结束。',
    icon: '🚀',
  },
  {
    title: '① 建产品与工艺',
    desc: '先在「主数据」里维护产品、工序和工艺路线。没有产品，后续订单和工单都无从谈起。\n\n左侧菜单 → 主数据 → 产品管理。',
    icon: '📦',
    action: { to: 'product', label: '去加一个产品' },
  },
  {
    title: '② 建客户订单',
    desc: '接到订单后在「生产」里创建客户订单，系统据此自动生成生产计划，再拆分为工单。\n\n左侧菜单 → 生产 → 生产计划。',
    icon: '🧾',
    action: { to: 'order', label: '去新建订单' },
  },
  {
    title: '③ 派工与报工',
    desc: '工单下发后给班组/员工派工，员工在 H5 或小程序里扫码报工，班组长审核，系统按工价自动算出工资，并在看板实时跟踪进度。',
    icon: '🏭',
    action: { to: 'report', label: '去看生产看板' },
  },
]

const actionMap: Record<string, string> = {
  product: tenantAdminPath('/master/products'),
  order: tenantAdminPath('/plans'),
  report: tenantAdminPath('/dashboard/kanban'),
}

function isDone() {
  try {
    return localStorage.getItem(GUIDE_KEY) === '1'
  } catch {
    return false
  }
}

function markDone() {
  try {
    localStorage.setItem(GUIDE_KEY, '1')
  } catch {
    /* ignore */
  }
}

/** 手动重开：清掉 done 标记并弹窗（用于帮助页"重新引导"） */
function openNow() {
  try {
    localStorage.removeItem(GUIDE_KEY)
  } catch {
    /* ignore */
  }
  current.value = 0
  show.value = true
}

/** 组件级手动调用入口（父组件可直接拿 ref 调） */
defineExpose({ openNow })

function close() {
  markDone()
  show.value = false
}

function next() {
  if (current.value === 0) {
    current.value = 1
    return
  }
  const act = steps[current.value]?.action
  if (act) {
    markDone()
    router.push(actionMap[act.to] ?? tenantAdminPath('/home'))
    show.value = false
  } else {
    current.value += 1
  }
}

function tryAutoShow() {
  if (!props.autoShow || isDone()) return
  setTimeout(() => {
    show.value = true
  }, 600)
}

function onReopen() {
  openNow()
}

onMounted(() => {
  tryAutoShow()
  window.addEventListener(REOPEN_EVENT, onReopen)
})

onUnmounted(() => {
  window.removeEventListener(REOPEN_EVENT, onReopen)
})

watch(
  () => props.autoShow,
  (v) => {
    if (v) tryAutoShow()
  }
)
</script>

<template>
  <Teleport to="body">
    <Transition name="guide-fade">
      <div v-if="show" class="guide-mask" @click.self="close">
        <div class="guide-card" role="dialog" aria-modal="true">
          <button class="guide-skip" type="button" @click="close">跳过引导</button>

          <div class="guide-icon">{{ steps[current].icon }}</div>
          <h3 class="guide-title">{{ steps[current].title }}</h3>
          <p class="guide-desc">{{ steps[current].desc }}</p>

          <div class="guide-footer">
            <div class="guide-dots">
              <span v-for="(s, i) in steps" :key="i" class="guide-dot" :class="{ active: i === current }" />
            </div>
            <div class="guide-actions">
              <el-button v-if="current === 0" type="primary" @click="next">
                {{ steps[current].action?.label || '开始使用' }}
              </el-button>
              <template v-else>
                <el-button v-if="current === 1 || current === 2" @click="current += 1">下一步</el-button>
                <el-button type="primary" @click="next">{{ steps[current].action?.label }}</el-button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.guide-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.guide-card {
  position: relative;
  width: 380px;
  max-width: 92vw;
  background: #fff;
  border-radius: 18px;
  padding: 32px 26px 22px;
  text-align: center;
  box-shadow: 0 16px 60px rgba(15, 23, 42, 0.28);
}
.guide-skip {
  position: absolute;
  top: 12px;
  right: 14px;
  border: none;
  background: none;
  font-size: 13px;
  color: #8a94a6;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.guide-skip:hover {
  background: #f1f5f9;
  color: #475569;
}
.guide-icon {
  font-size: 44px;
  margin-bottom: 12px;
}
.guide-title {
  font-size: 19px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 10px;
}
.guide-desc {
  font-size: 14px;
  line-height: 1.75;
  color: #475569;
  margin: 0;
  white-space: pre-line;
  text-align: left;
}
.guide-footer {
  margin-top: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.guide-dots {
  display: flex;
  gap: 6px;
  align-items: center;
}
.guide-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #d5dbe6;
  transition: all 0.2s;
}
.guide-dot.active {
  width: 22px;
  background: #2563eb;
}
.guide-actions {
  display: flex;
  gap: 8px;
}
.guide-fade-enter-active,
.guide-fade-leave-active {
  transition: opacity 0.2s ease;
}
.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
}
</style>