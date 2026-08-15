import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/OfficialLayout.vue'),
    children: [
      { path: '', name: 'siteHome', component: () => import('@/pages/official/OfficialLandingPage.vue') },
      { path: 'features', name: 'siteFeatures', component: () => import('@/pages/official/OfficialFeaturesPage.vue') },
      { path: 'workflow', name: 'siteWorkflow', component: () => import('@/pages/official/OfficialWorkflowPage.vue') },
      { path: 'about', name: 'siteAbout', component: () => import('@/pages/official/OfficialAboutPage.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
