<script setup lang="ts">
import type { Book } from '@/types/api'
import { RadioGroup, RadioGroupOption } from '@headlessui/vue'
import { BookOpenIcon, StarIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { useDebounceFn } from '@vueuse/core'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AppHeader from '@/components/AppHeader.vue'
import BookItem from '@/components/BookItem.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useBooksStore } from '@/stores/books'

const router = useRouter()
const booksStore = useBooksStore()

const isDeleteModalOpen = ref(false)
const bookToDelete = ref<Book | null>(null)
const deleteType = ref<'soft' | 'physical'>('physical')

onMounted(() => {
  // 初始化默认状态：未读完
  if (booksStore.finishedFilter === undefined) {
    booksStore.finishedFilter = false
  }
  if (booksStore.startedFilter === undefined) {
    booksStore.startedFilter = true
  }
  booksStore.fetchBooks()
})

const debouncedSearch = useDebounceFn(() => {
  booksStore.fetchBooks()
}, 300)

function onSearchInput() {
  debouncedSearch()
}

function openBook(book: Book) {
  router.push(`/reader/${book.id}`)
}

function toggleStar(book: Book) {
  booksStore.toggleStar(book.id!, !book.is_starred)
}

function confirmDelete(book: Book, type: 'soft' | 'physical' = 'physical') {
  bookToDelete.value = book
  deleteType.value = type
  isDeleteModalOpen.value = true
}

async function doDelete() {
  if (!bookToDelete.value)
    return

  try {
    const isPhysical = deleteType.value === 'physical'
    await booksStore.deleteBook(bookToDelete.value.id!, isPhysical)
  }
  catch (e) {
    console.error(e)
    toast.error('操作失败')
  }
  finally {
    isDeleteModalOpen.value = false
    bookToDelete.value = null
  }
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
const statusOptions = [
  { id: 'reading', label: '未读完', activeClass: 'text-blue-600 dark:text-blue-400' },
  { id: 'finished', label: '已读完', activeClass: 'text-green-600 dark:text-green-400' },
  { id: 'all', label: '全部', activeClass: 'text-gray-900 dark:text-white' },
]

function updateStatus(status: 'reading' | 'finished' | 'all') {
  currentStatus.value = status
  setStatusFilter(status)
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <!-- Header -->
    <AppHeader
      v-model:search-model-value="booksStore.searchQuery"
      title="我的书架"
      show-search
      search-placeholder="搜索书名..."
      @search-input="onSearchInput"
    >
      <template #bottom>
        <!-- Filters -->
        <div class="flex items-center gap-2 mt-3 overflow-x-auto no-scrollbar pb-1">
          <!-- Status Group (Using RadioGroup for A11y) -->
          <RadioGroup
            :model-value="currentStatus"
            class="flex p-1 bg-gray-100 dark:bg-gray-800 rounded-lg"
            @update:model-value="updateStatus"
          >
            <RadioGroupOption
              v-for="option in statusOptions"
              :key="option.id"
              v-slot="{ checked }"
              :value="option.id"
              class="focus:outline-none"
            >
              <button
                class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
                :class="[
                  checked
                    ? `bg-white dark:bg-gray-700 shadow-sm ${option.activeClass}`
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
                ]"
              >
                {{ option.label }}
              </button>
            </RadioGroupOption>
          </RadioGroup>

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
      </template>
    </AppHeader>

    <!-- Books List -->
    <main class="px-4 py-4">
      <SkeletonLoader v-if="booksStore.loading" type="list-item" />

      <EmptyState
        v-else-if="booksStore.filteredBooks.length === 0"
        title="暂无书籍"
        description="您的书架还是空的，去发现页面找一些好书吧"
        :icon="BookOpenIcon"
      >
        <template #actions>
          <button
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white rounded-xl text-sm font-medium transition-all shadow-sm"
            @click="router.push('/discovery')"
          >
            去发现
          </button>
        </template>
      </EmptyState>

      <div v-else class="space-y-3">
        <BookItem
          v-for="book in booksStore.filteredBooks"
          :key="book.id"
          :book="book"
          @open="openBook"
          @toggle-star="toggleStar"
          @remove="confirmDelete($event, 'soft')"
          @delete="confirmDelete($event, 'physical')"
        />
      </div>
    </main>
    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :show="isDeleteModalOpen"
      :title="deleteType === 'physical' ? '彻底删除书籍' : '移出书架'"
      :message="`确定要${deleteType === 'physical' ? '彻底删除' : '移出'} &quot;${bookToDelete?.title}&quot; 吗？`"
      :confirm-label="deleteType === 'physical' ? '彻底删除' : '移出'"
      :type="deleteType === 'physical' ? 'danger' : 'info'"
      @confirm="doDelete"
      @close="isDeleteModalOpen = false"
    >
      <template #extra>
        <span v-if="deleteType === 'physical'" class="text-red-500 font-medium block mt-2">
          此操作将删除物理文件，无法撤销！
        </span>
        <span v-else class="block mt-2">
          文件将保留在服务器上，后续可重新导入。
        </span>
      </template>
    </ConfirmModal>
  </div>
</template>
