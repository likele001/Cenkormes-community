<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
  }>(),
  { label: '管理后台预览' },
)
</script>

<template>
  <figure class="dash-preview" :aria-label="label">
    <div class="dash-preview__window">
      <div class="dash-preview__topbar">
        <span class="dash-preview__dots" aria-hidden="true"><i /><i /><i /></span>
        <span class="dash-preview__url">admin.lightmes.local</span>
      </div>
      <div class="dash-preview__body">
        <aside class="dash-preview__sidebar" aria-hidden="true">
          <div class="dash-preview__logo" />
          <div class="dash-preview__nav-item dash-preview__nav-item--active" />
          <div class="dash-preview__nav-item" />
          <div class="dash-preview__nav-item" />
          <div class="dash-preview__nav-item" />
        </aside>
        <div class="dash-preview__main">
          <div class="dash-preview__stats">
            <div class="dash-preview__stat dash-preview__stat--orange" />
            <div class="dash-preview__stat" />
            <div class="dash-preview__stat" />
            <div class="dash-preview__stat" />
          </div>
          <div class="dash-preview__chart" />
          <div class="dash-preview__table">
            <div class="dash-preview__row" />
            <div class="dash-preview__row" />
            <div class="dash-preview__row dash-preview__row--highlight" />
          </div>
        </div>
      </div>
    </div>
    <figcaption v-if="label" class="dash-preview__caption">{{ label }}</figcaption>
  </figure>
</template>

<style scoped>
.dash-preview { margin: 0; width: 100%; }
.dash-preview__window {
  border-radius: var(--lm-radius-lg);
  border: 1px solid var(--lm-border-strong);
  background: var(--lm-surface);
  overflow: hidden;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.04), 0 24px 48px rgba(0,0,0,0.1);
}
.dash-preview__topbar {
  display: flex; align-items: center; gap: var(--lm-space-3);
  padding: 10px 14px;
  background: var(--lm-bg-elevated);
  border-bottom: 1px solid var(--lm-border);
}
.dash-preview__dots { display: flex; gap: 5px; }
.dash-preview__dots i { width: 8px; height: 8px; border-radius: 50%; background: var(--lm-border-strong); }
.dash-preview__dots i:first-child { background: #ef4444; }
.dash-preview__dots i:nth-child(2) { background: #eab308; }
.dash-preview__dots i:nth-child(3) { background: #22c55e; }
.dash-preview__url { font-family: var(--lm-font-mono); font-size: 0.6875rem; color: var(--lm-text-muted); }
.dash-preview__body { display: grid; grid-template-columns: 56px 1fr; min-height: 220px; }
.dash-preview__sidebar { padding: 12px 8px; border-right: 1px solid var(--lm-border); display: flex; flex-direction: column; gap: 8px; }
.dash-preview__logo { height: 24px; border-radius: 6px; background: var(--lm-cta-soft); margin-bottom: 8px; }
.dash-preview__nav-item { height: 28px; border-radius: 6px; background: var(--lm-surface-muted); }
.dash-preview__nav-item--active { background: var(--lm-cta-soft); border: 1px solid rgb(249 115 22 / 0.3); }
.dash-preview__main { padding: 14px; display: flex; flex-direction: column; gap: 12px; }
.dash-preview__stats { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 8px; }
.dash-preview__stat { height: 48px; border-radius: 8px; background: var(--lm-surface-muted); border: 1px solid var(--lm-border); }
.dash-preview__stat--orange { background: var(--lm-cta-soft); border-color: rgb(249 115 22 / 0.25); }
.dash-preview__chart { flex: 1; min-height: 72px; border-radius: 10px; background: linear-gradient(180deg,var(--lm-accent-cyan-soft),transparent 70%); border: 1px solid var(--lm-border); }
.dash-preview__table { display: grid; gap: 6px; }
.dash-preview__row { height: 22px; border-radius: 5px; background: var(--lm-surface-muted); }
.dash-preview__row--highlight { background: var(--lm-cta-soft); }
.dash-preview__caption { margin-top: var(--lm-space-3); text-align: center; font-size: 0.8125rem; color: var(--lm-text-muted); }
@media (min-width: 64rem) { .dash-preview__body { min-height: 280px; } }
</style>
