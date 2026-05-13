import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/market',
  },
  {
    path: '/login',
    component: () => import('@/views/LoginView.vue'),
    meta: { nav: 'none', public: true },
  },
  {
    path: '/market',
    component: () => import('@/views/MarketView.vue'),
    meta: { nav: 'market', requiresAuth: true },
  },
  {
    path: '/news',
    component: () => import('@/views/NewsView.vue'),
    meta: { nav: 'news', requiresAuth: true },
  },
  {
    path: '/watch',
    component: () => import('@/views/WatchView.vue'),
    meta: { nav: 'watch', requiresAuth: true },
  },
  {
    path: '/strategy',
    component: () => import('@/views/StrategyView.vue'),
    meta: { nav: 'strategy', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && isLoggedIn) {
    next('/market')
  } else {
    next()
  }
})

export default router
