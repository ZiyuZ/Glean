<script setup lang="ts">
import { ArrowsRightLeftIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { computed, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FileTree from '@/components/FileTree.vue'
import ScanManager from '@/components/ScanManager.vue'
import { useBooksStore } from '@/stores/books'

const isScanManagerOpen = ref(false)
const booksStore = useBooksStore()
const searchQuery = ref('')

function onScanFinished() {
  booksStore.fetchBooks()
}

const filteredBooks = computed(() => {
  if (!searchQuery.value)
    return undefined // Pass undefined to let FileTree use store directly (or all books)

  const query = searchQuery.value.toLowerCase()
  return booksStore.books.filter(book =>
    book.title.toLowerCase().includes(query)
    || book.path.toLowerCase().includes(query),
  )
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20 flex flex-col">
    <!-- Header -->
    <AppHeader title="书库">
      <template #actions>
        <button
          class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          @click="isScanManagerOpen = true"
        >
          <ArrowsRightLeftIcon class="w-4 h-4" />
          扫描
        </button>
      </template>

      <template #bottom>
        <div class="mt-3 relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索文件或路径..."
            class="w-full pl-10 pr-10 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
          >
          <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <MagnifyingGlassIcon class="w-5 h-5" />
          </div>
          <button
            v-if="searchQuery"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            @click="searchQuery = ''"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </template>
    </AppHeader>

    <!-- Main Content -->
    <main class="px-4 py-4 max-w-5xl mx-auto flex flex-1 w-full">
      <FileTree class="flex-1 w-full" :books="filteredBooks" />
    </main>

    <!-- Scan Manager Dialog -->
    <ScanManager
      :is-open="isScanManagerOpen"
      @close="isScanManagerOpen = false"
      @scan-finished="onScanFinished"
    />
  </div>
</template>
