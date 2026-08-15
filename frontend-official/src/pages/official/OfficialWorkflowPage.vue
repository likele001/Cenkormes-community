<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PhonePreview from '@/components/official/PhonePreview.vue'
import DashboardPreview from '@/components/official/DashboardPreview.vue'
import { workflowSteps, salesPlans, saasPlans } from '@/data/official-content'

const h5Url = 'https://h5.mes.cenkor.cn'

// 6月24日新增：根据所选套餐展示对应能力（如 AI 报工仅 Pro/Enterprise 可见）
const selectedPlanId = ref<string>('saas-pro')
const currentPlan = () => salesPlans.find((p) => p.id === selectedPlanId.value) || saasPlans[1]

// 6月24日新增：扩展后的工作流步骤（含 AI 报工 / 行业包配置 / 数据看板）
const extendedSteps = ref<any[]>([])

function rebuildSteps() {
  const plan = currentPlan()
  const maxIndustries = plan.maxIndustries ?? 99
  const baseSteps = [
    { step: 1, title: '接单确认', tag: '客户 / 管理员', desc: '客户 H5 自助下单，或后台手工建单；确认后自动分解生产工单。', screen: 'home' as const },
    { step: 2, title: '行业包配置', tag: '管理员', desc: `按当前套餐（${plan.name}）可启用 ${maxIndustries < 0 ? '不限' : maxIndustries} 个行业包，确定工序 / 质检模板。`, screen: 'home' as const },
    { step: 3, title: '排产派工', tag: '计划员', desc: '按交期排产，生成任务二维码，推送到员工手机任务列表。', screen: 'tasks' as const },
    { step: 4, title: '扫码报工', tag: '一线员工', desc: '扫描任务码报工，上传完工证据，提交后即时显示预估工资。', screen: 'report' as const },
  ]
  if (plan.tier === 'pro' || plan.tier === 'enterprise') {
    baseSteps.push({
      step: 5,
      title: 'AI 智能报工',
      tag: 'AI Agent',
      desc: '照片自动计数、缺陷智能分类、语音录入转结构化报工。',
      screen: 'report' as const,
    })
  }
  baseSteps.push({
    step: 6,
    title: '审核算薪',
    tag: '班组长 / 质检',
    desc: '多级审核通过后自动算薪，支持电子工资条与签名确认。',
    screen: 'home' as const,
  })
  if (plan.tier === 'enterprise') {
    baseSteps.push({
      step: 7,
      title: '数据驾驶舱',
      tag: '老板 / 厂长',
      desc: '实时经营指标、车间大屏、逾期预警与 AI 经营分析。',
      screen: 'home' as const,
    })
  }
  extendedSteps.value = baseSteps
}

onMounted(() => {
  document.title = '生产流程 · 辰科MES'
  rebuildSteps()
})
</script>

<template>
  <div class="official-container official-container--narrow">
    <header class="official-page-head">
      <p class="official-section__eyebrow">生产流程</p>
      <h1 class="official-page-head__title">从下单到算薪</h1>
      <p class="official-page-head__desc">四个阶段串起加工厂日常闭环，PC 与手机在每个环节各司其职。</p>
    </header>

    <!-- 6月24日新增：套餐选择器 -->
    <div class="official-toolbar">
      <label>查看套餐：</label>
      <select v-model="selectedPlanId" class="official-select" @change="rebuildSteps">
        <option v-for="p in salesPlans" :key="p.id" :value="p.id">{{ p.name }}（¥{{ p.price }}{{ p.priceSuffix }}）</option>
      </select>
    </div>

    <section class="official-timeline" aria-label="生产流程">
      <article v-for="step in extendedSteps" :key="step.step" class="official-step">
        <div class="official-step__num">{{ step.step }}</div>
        <div>
          <span class="official-step__tag">{{ step.tag }}</span>
          <h2 class="official-step__title">{{ step.title }}</h2>
          <p class="official-step__desc">{{ step.desc }}</p>
        </div>
        <div class="official-step__preview">
          <PhonePreview v-if="step.step <= 5 && step.screen !== 'home'" :screen="step.screen" :label="step.step <= 2 ? '移动端' : '扫码报工'" />
          <DashboardPreview v-else :label="step.step === 7 ? 'PC 老板驾驶舱' : 'PC 审核算薪'" />
        </div>
      </article>
    </section>

    <aside class="official-cta">
      <p class="official-cta__title">从第一阶段开始</p>
      <p class="official-cta__desc">登录后创建或确认第一笔订单，系统自动分解工单。</p>
      <a class="official-btn official-btn--primary official-btn--block" :href="h5Url" target="_blank" rel="noopener">开始试用</a>
    </aside>

    <footer class="official-footer-bar"><p>流程细节以系统操作手册为准</p></footer>
  </div>
</template>
