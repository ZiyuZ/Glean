<script setup lang="ts">
import type { Book } from '@/types/api'
import { CheckCircleIcon, StarIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { useDebounceFn } from '@vueuse/core'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/books'

const router = useRouter()
const booksStore = useBooksStore()

// 初始加载：默认显示“未读完” (started=true, finished=false)
// 在 store 初始化时或此处设置
// 目前 store 默认 started=true, finished=undefined
// 我们调整为默认: started=true, finished=false

onMounted(() => {
  // 初始化默认状态：未读完
  if (booksStore.finishedFilter === undefined) {
    booksStore.finishedFilter = false
  }
  booksStore.fetchBooks()
})

const debouncedSearch = useDebounceFn(() => {
  booksStore.fetchBooks()
}, 300)

function onSearchInput() {
  debouncedSearch()
}

function formatDate(timestamp: number | null): string {
  if (!timestamp)
    return '未读'
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1)
    return '刚刚'
  if (minutes < 60)
    return `${minutes}分钟前`
  if (hours < 24)
    return `${hours}小时前`
  if (days === 1)
    return '昨天'
  if (days < 30)
    return `${days}天前`
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
  await booksStore.deleteBook(book.id!)
}

function toggleStarredFilter() {
  booksStore.starredFilter = booksStore.starredFilter === true ? undefined : true
  booksStore.fetchBooks()
}

// 状态筛选：'reading' (未读完) | 'finished' (已读完) | 'all' (全部已开始)
function setStatusFilter(status: 'reading' | 'finished' | 'all') {
  if (status === 'reading') {
    booksStore.startedFilter = true
    booksStore.finishedFilter = false
  }
  else if (status === 'finished') {
    booksStore.startedFilter = true
    booksStore.finishedFilter = true
  }
  else {
    // All (Started)
    booksStore.startedFilter = true
    booksStore.finishedFilter = undefined
  }
  booksStore.fetchBooks()
}

// 计算当前激活的状态
const currentStatus = ref<'reading' | 'finished' | 'all'>('reading')
// 监听 store 变化同步状态 (简单起见，setter 同步更新 currentStatus)
function updateStatus(status: 'reading' | 'finished' | 'all') {
  currentStatus.value = status
  setStatusFilter(status)
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

        <!-- Search -->
        <div class="mt-3 relative">
          <input
            v-model="booksStore.searchQuery"
            type="text"
            placeholder="搜索书名..."
            class="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
            @input="onSearchInput"
          >
          <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
              <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex items-center gap-2 mt-3 overflow-x-auto no-scrollbar pb-1">
          <!-- Status Group -->
          <div class="flex p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <button
              class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
              :class="[
                currentStatus === 'reading'
                  ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
              ]"
              @click="updateStatus('reading')"
            >
              未读完
            </button>
            <button
              class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
              :class="[
                currentStatus === 'finished'
                  ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
              ]"
              @click="updateStatus('finished')"
            >
              已读完
            </button>
            <button
              class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
              :class="[
                currentStatus === 'all'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
              ]"
              @click="updateStatus('all')"
            >
              全部
            </button>
          </div>

          <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

          <!-- Starred Toggle -->
          <button
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1 border border-transparent"
            :class="[
              booksStore.starredFilter === true
                ? 'bg-yellow-50 text-yellow-600 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-500 dark:border-yellow-900/50'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700',
            ]"
            @click="toggleStarredFilter"
          >
            <component :is="booksStore.starredFilter === true ? StarIconSolid : StarIcon" class="w-4 h-4" />
            收藏
          </button>
        </div>
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
                <StarIconSolid v-if="book.is_starred" class="w-[16px] h-[16px] text-yellow-500" title="已收藏" />
                <CheckCircleIcon v-if="book.is_finished" class="w-[16px] h-[16px] text-green-500" title="已读完" />
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
                <component :is="book.is_starred ? StarIconSolid : StarIcon" class="w-[20px] h-[20px]" />
              </button>
              <button
                class="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                @click.stop="deleteBook(book, $event)"
              >
                <TrashIcon class="w-[20px] h-[20px]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
