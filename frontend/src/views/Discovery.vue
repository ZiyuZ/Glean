<script setup lang="ts">
import type { Book } from '@/types/api'
import { ArrowPathIcon, CheckCircleIcon, ClockIcon, DocumentTextIcon, StarIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/books'

const router = useRouter()
const booksStore = useBooksStore()

const randomBooks = ref<Book[]>([])
const loading = ref(false)

onMounted(() => {
  loadRandomBooks()
})

async function loadRandomBooks() {
  loading.value = true
  try {
    randomBooks.value = await booksStore.fetchRandomBooks(8)
  }
  finally {
    loading.value = false
  }
}

function openBook(book: Book) {
  router.push(`/reader/${book.id}`)
}

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

function formatFileSize(bytes: number): string {
  if (bytes === 0)
    return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / k ** i).toFixed(1)} ${sizes[i]}`
}

function toggleStar(book: Book, event: Event) {
  event.stopPropagation()
  booksStore.toggleStar(book.id!, !book.is_starred).then(() => {
    // 更新本地状态
    const index = randomBooks.value.findIndex(b => b.id === book.id)
    if (index !== -1 && randomBooks.value[index]) {
      randomBooks.value[index].is_starred = !book.is_starred
    }
  })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <header
      class="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/95 dark:border-gray-800"
    >
      <div class="px-4 py-3 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            发现
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            从书库中随机发现好书
          </p>
        </div>
        <button
          :disabled="loading"
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 disabled:opacity-50 transition-colors"
          title="换一批"
          @click="loadRandomBooks"
        >
          <ArrowPathIcon class="w-6 h-6" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </header>

    <!-- Random Books -->
    <main class="px-4 py-4">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          加载中...
        </p>
      </div>

      <div v-else-if="randomBooks.length === 0" class="text-center py-12">
        <p class="text-gray-500 dark:text-gray-400">
          暂无书籍
        </p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="book in randomBooks" :key="book.id" class="bg-white dark:bg-gray-800 rounded-xl p-4  flex flex-col justify-between shadow-sm hover:shadow-lg transition-all cursor-pointer border border-gray-200 dark:border-gray-700"
          @click="openBook(book)"
        >
          <!-- Header with title and star -->
          <div class="flex items-start justify-between mb-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white line-clamp-2 flex-1 pr-2">
              {{ book.title }}
            </h3>
            <button
              class="p-1.5 rounded-lg transition-colors flex-shrink-0" :class="[
                book.is_starred
                  ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                  : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700',
              ]" @click.stop="toggleStar(book, $event)"
            >
              <component :is="book.is_starred ? StarIconSolid : StarIcon" class="size-[18px]" />
            </button>
          </div>

          <!-- Book info -->
          <div class="space-y-2">
            <!-- File size -->
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <DocumentTextIcon class="size-[14px] flex-shrink-0" />
              <span>{{ formatFileSize(book.file_size) }}</span>
            </div>

            <!-- Last read time -->
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <ClockIcon class="size-[14px] flex-shrink-0" />
              <span>{{ formatDate(book.last_read_time) }}</span>
            </div>

            <!-- Status badges -->
            <div class="flex items-center gap-2 pt-1 h-6">
              <span
                v-if="book.is_starred"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
              >
                <StarIconSolid class="size-[12px]" />
                已收藏
              </span>
              <span
                v-if="book.is_finished"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
              >
                <CheckCircleIcon class="size-[12px]" />
                已读完
              </span>
              <span
                v-if="book.chapter_index !== null"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
              >
                阅读中
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
