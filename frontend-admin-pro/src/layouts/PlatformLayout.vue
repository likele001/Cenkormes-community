<template>
  <el-container class="h-screen w-screen bg-[var(--admin-page-bg)]">
    <el-aside
      :width="collapsed ? 'var(--admin-sider-collapsed-width)' : 'var(--admin-sider-width)'"
      class="admin-sider shrink-0 flex flex-col border-r border-[var(--admin-sider-border)] bg-[var(--admin-sider-bg)] transition-[width] duration-200 hidden md:flex"
      :class="{ 'admin-sider--collapsed': collapsed }"
    >
      <div class="admin-sider__brand h-14 px-4 flex items-center border-b border-[var(--admin-sider-border)]">
        <AdminBrand title="辰科MES" :subtitle="t('layout.saasSubtitle')" :use-tenant="false" :compact="collapsed" />
      </div>
      <el-menu
        class="admin-sider-menu border-0 flex-1 overflow-y-auto py-2"
        :default-active="route.path"
        :collapse="collapsed"
        router
      >
        <el-menu-item index="/platform/tenants">
          <el-icon><OfficeBuilding /></el-icon>
          <span>{{ t('menu.tenants') }}</span>
        </el-menu-item>
        <el-menu-item index="/platform/packages">
          <el-icon><Box /></el-icon>
          <span>{{ t('menu.packages') }}</span>
        </el-menu-item>
        <el-menu-item index="/platform/subscription-orders">
          <el-icon><Tickets /></el-icon>
          <span>{{ t('menu.subscriptionOrders') }}</span>
        </el-menu-item>
        <el-menu-item index="/platform/settings">
          <el-icon><Setting /></el-icon>
          <span>{{ t('menu.platformSettings') }}</span>
        </el-menu-item>
        <el-menu-item index="/platform/ai-models">
          <el-icon><MagicStick /></el-icon>
          <span>{{ t('menu.aiModels') }}</span>
        </el-menu-item>
        <el-menu-item index="/platform/profile">
          <el-icon><User /></el-icon>
          <span>{{ t('layout.personalCenter') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="min-w-0 min-h-0 flex flex-col">
      <el-header
        height="52px"
        class="admin-header flex items-center justify-between gap-3 px-3 sm:px-5 shrink-0 bg-[var(--admin-header-bg)] border-b border-[var(--admin-sider-border)]"
      >
        <div class="flex items-center gap-2 min-w-0">
          <el-button type="primary" link class="!px-1 hidden md:inline-flex" @click="toggleCollapse">
            <el-icon :size="20"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </el-button>
          <span class="text-sm text-[var(--admin-brand-subtitle)] truncate">{{ t('layout.platformOperation') }}</span>
        </div>
        <div class="flex items-center gap-1 sm:gap-2 shrink-0">
          <el-tooltip :content="isDark ? t('common.lightMode') : t('common.darkMode')" placement="bottom">
            <el-button type="primary" link class="!px-2" @click="toggleTheme">
              <el-icon :size="18"><Sunny v-if="isDark" /><Moon v-else /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button size="small" plain @click="router.push('/platform/profile')">{{ t('layout.personalCenter') }}</el-button>
          <el-button size="small" plain @click="logout">{{ t('layout.logout') }}</el-button>
        </div>
      </el-header>
      <el-main class="admin-main !p-3 sm:!p-5 min-h-0 overflow-y-auto">
        <div class="max-w-[1480px] mx-auto w-full min-w-0">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Box,
  Expand,
  Fold,
  MagicStick,
  Moon,
  OfficeBuilding,
  Setting,
  Sunny,
  Tickets,
  User,
} from '@element-plus/icons-vue'
import AdminBrand from '@/components/AdminBrand.vue'
import { useAdminTheme } from '@/composables/useAdminTheme'
import { useSidebarCollapse } from '@/composables/useSidebarCollapse'
import { setPlatformToken } from '@/api/platform'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { toggleTheme, isDark } = useAdminTheme()
const { collapsed, toggleCollapse } = useSidebarCollapse()

function logout() {
  setPlatformToken('')
  router.replace('/platform/login')
}
</script>

<style scoped>
.admin-main {
  background: var(--admin-page-bg);
}
</style>
