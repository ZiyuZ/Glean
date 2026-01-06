<script setup lang="ts">
import type { Book } from '@/types/api'
import { ArrowPathIcon, CheckCircleIcon, ClockIcon, DocumentTextIcon, StarIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
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
  <div class="h-full overflow-y-auto">
    <!-- Header -->
    <AppHeader
      title="发现"
      subtitle="从书库中随机发现好书"
      :action-icon="ArrowPathIcon"
      :action-loading="loading"
      action-title="换一批"
      @action="loadRandomBooks"
    />

    <!-- Random Books -->
    <main class="px-4 py-4">
      <SkeletonLoader v-if="loading" type="card" :count="8" />

      <EmptyState
        v-else-if="randomBooks.length === 0"
        title="暂无书籍"
        description="书库中还没有发现任何书籍，尝试扫描文件夹？"
        :icon="DocumentTextIcon"
      />

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
            <div class="flex items-center gap-1 flex-shrink-0">
              <span v-if="book.is_finished" title="已读完" class="text-green-500 dark:text-green-400 p-1.5">
                <CheckCircleIcon class="size-[18px]" />
              </span>
              <span v-else-if="book.chapter_index !== null" title="阅读中" class="text-blue-500 dark:text-blue-400 p-1.5">
                <ClockIcon class="size-[18px]" />
              </span>
              <button
                class="p-1.5 rounded-lg transition-colors" :class="[
                  book.is_starred
                    ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                    : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700',
                ]" @click.stop="toggleStar(book, $event)"
              >
                <component :is="book.is_starred ? StarIconSolid : StarIcon" class="size-[18px]" />
              </button>
            </div>
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
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
