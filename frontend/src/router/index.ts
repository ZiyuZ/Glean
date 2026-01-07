import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import Bookshelf from '@/views/Bookshelf.vue'
import Discovery from '@/views/Discovery.vue'
import Library from '@/views/Library.vue'
import Login from '@/views/Login.vue'
import Reader from '@/views/Reader.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'bookshelf',
      component: Bookshelf,
      meta: { title: '书架' },
    },
    {
      path: '/discovery',
      name: 'discovery',
      component: Discovery,
      meta: { title: '发现' },
    },
    {
      path: '/library',
      name: 'library',
      component: Library,
      meta: { title: '书库' },
    },
    {
      path: '/reader/:bookId',
      name: 'reader',
      component: Reader,
      meta: { title: '阅读', hideNav: true },
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { title: '验证', hideNav: true },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 确保 Auth 状态已初始化
  if (!authStore.isInitialized) {
    await authStore.init()
  }

  // 如果需要验证且未登录
  if (to.name !== 'login' && authStore.isAuthEnabled && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // 如果已登录但访问登录页
  if (to.name === 'login' && authStore.isAuthenticated) {
    const redirect = to.query.redirect as string
    next(redirect || '/')
    return
  }

  document.title = to.meta.title ? `${to.meta.title} - Glean` : 'Glean'
  next()
})

export default router
