<script setup lang="ts">
import { useRoute } from 'vue-router'
import '@/styles/official.css'

const h5Url = 'https://h5.mes.cenkor.cn'

const route = useRoute()

const navItems = [
  { path: '/', label: '首页' },
  { path: '/features', label: '功能' },
  { path: '/workflow', label: '流程' },
  { path: '/about', label: '关于' },
] as const

const tabs = [
  { path: '/', label: '首页', icon: 'home' },
  { path: '/features', label: '功能', icon: 'grid' },
  { path: '/workflow', label: '流程', icon: 'flow' },
  { path: '/about', label: '关于', icon: 'info' },
] as const

function isActive(tabPath: string): boolean {
  if (tabPath === '/') return route.path === '/' || route.path === ''
  return route.path.startsWith(tabPath)
}

function goToH5Login() {
  window.location.href = h5Url
}

function openRegister() {
  window.location.href = 'https://admin.mes.cenkor.cn/register/'
}
</script>

<template>
  <div class="official-root">
    <header class="official-header">
      <router-link class="official-brand" to="/">
        <span class="official-brand__mark">LM</span>
        <div>
          <span class="official-brand__name">辰科MES</span>
          <span class="official-brand__tag">MES 产品家族 · 辰科MES / CenkorMES</span>
        </div>
      </router-link>

      <nav class="official-nav-desktop" aria-label="主导航">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="official-nav-desktop__link"
          :class="{ 'is-active': isActive(item.path) }"
        >{{ item.label }}</router-link>
      </nav>

      <div class="official-header__actions">
        <button class="official-header__trial" type="button" @click="openRegister">注册试用</button>
        <a class="official-header__login" href="https://ck.mes.cenkor.cn" target="_blank" rel="noopener">CenkorMES 系统</a>
        <button class="official-header__login" type="button" @click="goToH5Login">登录系统</button>
      </div>
    </header>

    <main class="official-main">
      <router-view />
    </main>

    <nav class="official-tabbar" aria-label="移动端导航">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="official-tab"
        :class="{ 'is-active': isActive(tab.path) }"
      >
        <svg v-if="tab.icon === 'home'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="m3 10.5 9-7 9 7" /><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5" />
        </svg>
        <svg v-else-if="tab.icon === 'grid'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
        <svg v-else-if="tab.icon === 'flow'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M4 6h16M4 12h10M4 18h14" /><circle cx="18" cy="12" r="2" /><circle cx="20" cy="18" r="2" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="12" cy="12" r="9" /><path d="M12 16v-4M12 8h.01" />
        </svg>
        <span>{{ tab.label }}</span>
      </router-link>
      <a class="official-tab" href="https://ck.mes.cenkor.cn" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
        <span>CenkorMES</span>
      </a>
    </nav>
  </div>
</template>
