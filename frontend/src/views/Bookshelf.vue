<script setup lang="ts">
import type { Book } from '@/types/api'
import { CheckCircle2, Star, Trash2 } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/books'

const router = useRouter()
const booksStore = useBooksStore()

const showMenu = ref<number | null>(null)

onMounted(() => {
  booksStore.fetchBooks()
})

function formatDate(timestamp: number | null): string {
  if (!timestamp)
    return '未读'
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0)
    return '今天'
  if (days === 1)
    return '昨天'
  if (days < 7)
    return `${days}天前`
  if (days < 30)
    return `${Math.floor(days / 7)}周前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function openBook(book: Book) {
  router.push(`/reader/${book.id}`)
}

function toggleStar(book: Book, event: Event) {
  event.stopPropagation()
  booksStore.toggleStar(book.id!, !book.is_starred)
}

async function deleteBook(book: Book, event: Event) {
  event.stopPropagation()
  // if (confirm(`确定要删除《${book.title}》吗？`)) {
  await booksStore.deleteBook(book.id!)
  // }
  showMenu.value = null
}

function toggleFilter(type: 'starred' | 'finished') {
  if (type === 'starred') {
    booksStore.starredFilter
      = booksStore.starredFilter === undefined
        ? true
        : booksStore.starredFilter === true
          ? undefined
          : true
  }
  else {
    booksStore.finishedFilter
      = booksStore.finishedFilter === undefined
        ? false
        : booksStore.finishedFilter === false
          ? undefined
          : false
  }
  booksStore.fetchBooks()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <header
      class="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/95 dark:border-gray-800"
    >
      <div class="px-4 py-3">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          我的书架
        </h1>
        <div class="flex gap-2 mt-3">
          <button
            class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center gap-1" :class="[
              booksStore.starredFilter === true
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
            ]" @click="toggleFilter('starred')"
          >
            <Star :size="14" :fill="booksStore.starredFilter === true ? 'currentColor' : 'none'" />
            已收藏
          </button>
          <button
            class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center gap-1" :class="[
              booksStore.finishedFilter === false
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
            ]" @click="toggleFilter('finished')"
          >
            <CheckCircle2 :size="14" />
            未读完
          </button>
        </div>
        <input
          v-model="booksStore.searchQuery" type="text" placeholder="搜索书名..." class="w-full mt-3 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="booksStore.fetchBooks()"
        >
      </div>
    </header>

    <!-- Books List -->
    <main class="px-4 py-4">
      <div v-if="booksStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          加载中...
        </p>
      </div>

      <div v-else-if="booksStore.filteredBooks.length === 0" class="text-center py-12">
        <p class="text-gray-500 dark:text-gray-400">
          暂无书籍
        </p>
        <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">
          去发现页面找一些好书吧
        </p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="book in booksStore.filteredBooks" :key="book.id" class="relative bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
          @click="openBook(book)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {{ book.title }}
              </h2>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ formatDate(book.last_read_time) }}
              </p>
              <div class="flex items-center gap-2 mt-2">
                <Star v-if="book.is_starred" :size="16" class="text-yellow-500" fill="currentColor" title="已收藏" />
                <CheckCircle2 v-if="book.is_finished" :size="16" class="text-green-500" title="已读完" />
              </div>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                class="p-2 rounded-lg transition-colors" :class="[
                  book.is_starred
                    ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                    : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700',
                ]" @click.stop="toggleStar(book, $event)"
              >
                <Star :size="20" :fill="book.is_starred ? 'currentColor' : 'none'" />
              </button>
              <button
                class="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                @click.stop="deleteBook(book, $event)"
              >
                <Trash2 :size="20" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
