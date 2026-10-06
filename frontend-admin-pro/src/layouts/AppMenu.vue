<template>
  <el-menu
    class="admin-sider-menu border-0"
    :class="menuRootClass"
    :default-active="active"
    :collapse="layout === 'sider' && collapse"
    router
  >
    <el-menu-item index="/home">
      <el-icon><House /></el-icon>
      <span>{{ t('menu.home') }}</span>
    </el-menu-item>

    <el-sub-menu index="system" v-if="systemItems.length">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>{{ t('menu.system') }}</span>
      </template>
      <el-menu-item v-for="it in systemItems" :key="it.path" :index="it.path">
        <el-icon><component :is="it.icon" /></el-icon>
        <span>{{ t(it.i18nKey) }}</span>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="master" v-if="masterItems.length">
      <template #title>
        <el-icon><Box /></el-icon>
        <span>{{ t('menu.master') }}</span>
      </template>
      <el-menu-item v-for="it in masterItems" :key="it.path" :index="it.path">
        <el-icon><component :is="it.icon" /></el-icon>
        <span>{{ t(it.i18nKey) }}</span>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="production" v-if="productionItems.length">
      <template #title>
        <el-icon><Operation /></el-icon>
        <span>{{ t('menu.production') }}</span>
      </template>
      <el-menu-item v-for="it in productionItems" :key="it.path" :index="it.path">
        <el-icon><component :is="it.icon" /></el-icon>
        <span>{{ t(it.i18nKey) }}</span>
      </el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  House, Setting, Box, Operation, User, Key, Lock, OfficeBuilding, Tools, Bell,
  CollectionTag, FolderOpened, Goods, Grid, Share, DocumentCopy, List, UserFilled, EditPen,
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = withDefaults(
  defineProps<{ layout?: 'sider' | 'drawer'; collapse?: boolean }>(),
  { layout: 'sider', collapse: false },
)

const menuRootClass = computed(() =>
  props.layout === 'sider' ? 'h-full min-h-0 overflow-y-auto' : 'pb-2',
)

type MenuItem = { path: string; i18nKey: string; permissions?: string[]; icon: Component }

const route = useRoute()
const auth = useAuthStore()
const active = computed(() => route.path)

const systemAll: MenuItem[] = [
  { path: '/system/users', i18nKey: 'menu.users', permissions: ['user.manage'], icon: User },
  { path: '/system/roles', i18nKey: 'menu.roles', permissions: ['role.manage'], icon: Key },
  { path: '/system/permissions', i18nKey: 'menu.permissions', permissions: ['permission.manage'], icon: Lock },
  { path: '/system/departments', i18nKey: 'menu.departments', permissions: ['department.manage'], icon: OfficeBuilding },
  { path: '/system/settings', i18nKey: 'menu.settings', permissions: ['setting.manage'], icon: Tools },
  { path: '/system/notifications', i18nKey: 'menu.notifications', permissions: ['notification.view'], icon: Bell },
  { path: '/system/dictionary', i18nKey: 'menu.dictionary', permissions: ['dict.manage'], icon: CollectionTag },
  { path: '/system/attachments', i18nKey: 'menu.attachments', permissions: ['attachment.view'], icon: FolderOpened },
]

const masterAll: MenuItem[] = [
  { path: '/master/products', i18nKey: 'menu.products', permissions: ['product.manage'], icon: Goods },
  { path: '/master/skus', i18nKey: 'menu.skus', permissions: ['sku.manage'], icon: Grid },
  { path: '/master/processes', i18nKey: 'menu.processes', permissions: ['process.manage'], icon: Operation },
  { path: '/master/process-routes', i18nKey: 'menu.processRoutes', permissions: ['product.manage'], icon: Share },
]

const productionAll: MenuItem[] = [
  { path: '/production/orders', i18nKey: 'menu.orders', permissions: ['order.manage'], icon: DocumentCopy },
  { path: '/production/work-orders', i18nKey: 'menu.workOrders', permissions: ['work.manage'], icon: List },
  { path: '/production/tasks', i18nKey: 'menu.tasks', permissions: ['task.manage', 'dispatch.manage'], icon: List },
  { path: '/production/assignments', i18nKey: 'menu.assignments', permissions: ['dispatch.manage'], icon: UserFilled },
  { path: '/production/reports', i18nKey: 'menu.reports', permissions: ['report.audit'], icon: EditPen },
]

const systemItems = computed(() => systemAll.filter((x) => auth.hasAnyPermission(x.permissions)))
const masterItems = computed(() => masterAll.filter((x) => auth.hasAnyPermission(x.permissions)))
const productionItems = computed(() => productionAll.filter((x) => auth.hasAnyPermission(x.permissions)))
</script>
