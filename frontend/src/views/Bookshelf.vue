<script setup lang="ts">
import type { Book } from '@/types/api'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ExclamationTriangleIcon, StarIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { useDebounceFn } from '@vueuse/core'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import BookItem from '@/components/BookItem.vue'
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
    toast.success(isPhysical ? '书籍文件已彻底删除' : '已移出书架')
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
    <TransitionRoot as="template" :show="isDeleteModalOpen">
      <Dialog as="div" class="relative z-50" @close="isDeleteModalOpen = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div class="sm:flex sm:items-start">
                  <div
                    class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full sm:mx-0 sm:h-10 sm:w-10"
                    :class="deleteType === 'physical' ? 'bg-red-100' : 'bg-blue-100'"
                  >
                    <ExclamationTriangleIcon
                      class="h-6 w-6"
                      :class="deleteType === 'physical' ? 'text-red-600' : 'text-blue-600'"
                      aria-hidden="true"
                    />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
                      {{ deleteType === 'physical' ? '彻底删除书籍' : '移出书架' }}
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        确定要{{ deleteType === 'physical' ? '彻底删除' : '移出' }} "<strong>{{ bookToDelete?.title }}</strong>" 吗？
                        <span v-if="deleteType === 'physical'" class="text-red-500 font-medium block mt-1">此操作将删除物理文件，无法撤销！</span>
                        <span v-else class="block mt-1">文件将保留在服务器上，后续可重新导入。</span>
                      </p>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white shadow-sm sm:ml-3 sm:w-auto transition-colors"
                    :class="deleteType === 'physical' ? 'bg-red-600 hover:bg-red-500' : 'bg-blue-600 hover:bg-blue-500'"
                    @click="doDelete"
                  >
                    {{ deleteType === 'physical' ? '彻底删除' : '移出' }}
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white dark:bg-gray-700 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 sm:mt-0 sm:w-auto"
                    @click="isDeleteModalOpen = false"
                  >
                    取消
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>
