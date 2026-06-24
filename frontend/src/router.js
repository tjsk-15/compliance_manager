import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/insurance',
    name: 'insurance',
    component: () => import('@/pages/TrackerPage.vue'),
    meta: { tracker: 'insurance' },
  },
  {
    path: '/licence',
    name: 'licence',
    component: () => import('@/pages/TrackerPage.vue'),
    meta: { tracker: 'licence' },
  },
  {
    path: '/trademark',
    name: 'trademark',
    component: () => import('@/pages/TrackerPage.vue'),
    meta: { tracker: 'trademark' },
  },
  {
    path: '/compliance-records',
    name: 'compliance',
    component: () => import('@/pages/TrackerPage.vue'),
    meta: { tracker: 'compliance' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { managerOnly: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/compliance'),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
