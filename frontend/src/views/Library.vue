<script setup lang="ts">
import { WrenchScrewdriverIcon } from '@heroicons/vue/24/outline'
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
  <div class="h-full flex flex-col overflow-hidden">
    <!-- Header -->
    <AppHeader
      v-model:search-model-value="searchQuery"
      title="书库"
      :action-icon="WrenchScrewdriverIcon"
      action-title="管理"
      show-search
      search-placeholder="搜索文件或路径..."
      @action="isScanManagerOpen = true"
    />

    <!-- Main Content -->
    <main class="px-4 py-4 max-w-5xl mx-auto flex flex-1 w-full min-h-0">
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
