<script setup lang="ts">
type Screen = 'home' | 'report' | 'tasks'

withDefaults(
  defineProps<{
    screen?: Screen
    label?: string
  }>(),
  { screen: 'home', label: '员工端预览' },
)
</script>

<template>
  <figure class="phone-preview" :aria-label="label">
    <div class="phone-preview__shell">
      <div class="phone-preview__notch" aria-hidden="true" />
      <div class="phone-preview__screen">
        <template v-if="screen === 'home'">
          <div class="pp-banner">
            <span class="pp-banner__date">今日工作概况</span>
            <div class="pp-stats">
              <div><strong>—</strong><span>合格</span></div>
              <div><strong>—</strong><span>不良</span></div>
              <div><strong>—</strong><span>良率</span></div>
            </div>
          </div>
          <div class="pp-card">
            <div class="pp-line pp-line--lg" />
            <div class="pp-line" />
            <div class="pp-grid">
              <div class="pp-tile pp-tile--blue" />
              <div class="pp-tile pp-tile--green" />
              <div class="pp-tile pp-tile--orange" />
            </div>
          </div>
        </template>
        <template v-else-if="screen === 'report'">
          <div class="pp-scan">
            <div class="pp-scan__frame" />
            <p>对准任务二维码</p>
          </div>
          <div class="pp-card">
            <div class="pp-line pp-line--lg" />
            <div class="pp-line" />
            <div class="pp-btn" />
          </div>
        </template>
        <template v-else>
          <div class="pp-card">
            <div class="pp-line pp-line--lg" />
            <div class="pp-task" />
            <div class="pp-task" />
            <div class="pp-task pp-task--active" />
          </div>
        </template>
      </div>
    </div>
    <figcaption v-if="label" class="phone-preview__caption">{{ label }}</figcaption>
  </figure>
</template>

<style scoped>
.phone-preview { margin: 0; display: flex; flex-direction: column; align-items: center; gap: var(--lm-space-3); }
.phone-preview__shell { width: min(100%,220px); aspect-ratio: 9/19; border-radius: 28px; border: 2px solid var(--lm-border-strong); background: var(--lm-surface); padding: 10px 8px 12px; box-shadow: 0 0 0 1px rgba(0,0,0,0.04), 0 20px 40px rgba(0,0,0,0.12); position: relative; }
.phone-preview__notch { width: 72px; height: 18px; margin: 0 auto 8px; border-radius: 0 0 12px 12px; background: var(--lm-border-strong); }
.phone-preview__screen { height: calc(100% - 26px); border-radius: 18px; background: var(--lm-bg); overflow: hidden; padding: 8px; display: flex; flex-direction: column; gap: 8px; }
.phone-preview__caption { font-size: 0.75rem; color: var(--lm-text-muted); }
.pp-banner { border-radius: 12px; background: linear-gradient(135deg,#3b82f6,#2563eb); color: #fff; padding: 10px; }
.pp-banner__date { font-size: 0.625rem; opacity: 0.85; }
.pp-stats { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 4px; margin-top: 8px; text-align: center; }
.pp-stats strong { display: block; font-size: 0.875rem; }
.pp-stats span { font-size: 0.5625rem; opacity: 0.8; }
.pp-card { background: var(--lm-surface-muted); border: 1px solid var(--lm-border); border-radius: 10px; padding: 8px; flex: 1; }
.pp-line { height: 6px; border-radius: 4px; background: var(--lm-border); margin-bottom: 6px; width: 70%; }
.pp-line--lg { width: 45%; height: 8px; }
.pp-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 4px; margin-top: 8px; }
.pp-tile { aspect-ratio: 1; border-radius: 8px; }
.pp-tile--blue { background: rgb(37 99 235 / 0.25); }
.pp-tile--green { background: rgb(34 197 94 / 0.25); }
.pp-tile--orange { background: var(--lm-cta-soft); }
.pp-scan { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: var(--lm-text-muted); font-size: 0.625rem; }
.pp-scan__frame { width: 72px; height: 72px; border: 2px dashed var(--lm-cta); border-radius: 10px; }
.pp-btn { height: 24px; border-radius: 8px; background: var(--lm-cta); margin-top: 8px; }
.pp-task { height: 28px; border-radius: 8px; background: var(--lm-surface-muted); margin-bottom: 6px; }
.pp-task--active { background: var(--lm-cta-soft); border: 1px solid rgb(249 115 22 / 0.35); }
</style>
