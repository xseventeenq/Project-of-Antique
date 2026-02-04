/*
 * Vue Router 配置
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/borrow',
    name: 'Borrow',
    component: () => import('@/views/Borrow.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/return',
    name: 'Return',
    component: () => import('@/views/Return.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/borrow-records',
    name: 'BorrowRecords',
    component: () => import('@/views/BorrowRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/return-records',
    name: 'ReturnRecords',
    component: () => import('@/views/ReturnRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/artifacts/:id',
    name: 'ArtifactDetail',
    component: () => import('@/views/ArtifactDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/report/:id',
    name: 'ReportDetail',
    component: () => import('@/views/ReportDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  // 需要认证的页面
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 已登录用户访问登录页，跳转到首页
  if (to.path === '/login' && token) {
    next('/')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin) {
    const userRole = localStorage.getItem('userRole')
    if (userRole !== 'admin') {
      next('/')
      return
    }
  }

  next()
})

export default router
