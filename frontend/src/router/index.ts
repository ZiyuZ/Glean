import { createRouter, createWebHistory } from 'vue-router'
import Bookshelf from '@/views/Bookshelf.vue'
import Discovery from '@/views/Discovery.vue'
import Management from '@/views/Management.vue'
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
      path: '/management',
      name: 'management',
      component: Management,
      meta: { title: '管理' },
    },
    {
      path: '/reader/:bookId',
      name: 'reader',
      component: Reader,
      meta: { title: '阅读', hideNav: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - Glean` : 'Glean'
  next()
})

export default router
