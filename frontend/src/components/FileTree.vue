<script lang="ts">
</script>

<script setup lang="ts">
import type { Book } from '@/types/api'
import { FolderIcon } from '@heroicons/vue/24/outline'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import TreeItem from '@/components/TreeItem.vue'
import { useBooksStore } from '@/stores/books'

export interface TreeNode {
  name: string
  path: string
  type: 'folder' | 'file'
  children?: TreeNode[]
  data?: Book
}

const props = defineProps<{
  books?: Book[]
}>()

const router = useRouter()
const booksStore = useBooksStore()

const nodes = ref<TreeNode[]>([])

const booksSource = computed(() => props.books ?? booksStore.books)

onMounted(async () => {
  // Only manage store filtering/fetching if we are using the store directly (no props provided)
  if (!props.books) {
    // Reset filters to show all books
    booksStore.startedFilter = undefined
    booksStore.finishedFilter = undefined
    booksStore.starredFilter = undefined

    if (booksStore.books.length === 0) {
      await booksStore.fetchBooks()
    }
    else {
      // Force refresh to ensure we have all books
      await booksStore.fetchBooks()
    }
  }
})

watch(booksSource, (newBooks) => {
  buildTree(newBooks)
}, { deep: true, immediate: true })

function buildTree(books: Book[]) {
  const root: TreeNode[] = []

  for (const book of books) {
    // book.path is relative, e.g. "Author/Series/Book.txt" or just "Book.txt"
    const parts = book.path.split(/[\\/]/) // Handle both slash types
    let currentLevel = root

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]
      const isFile = i === parts.length - 1
      const existingNode = currentLevel.find(n => n.name === part && n.type === (isFile ? 'file' : 'folder'))

      if (existingNode) {
        if (!isFile) {
          currentLevel = existingNode.children!
        }
      }
      else {
        const newNode: TreeNode = {
          name: part || '',
          path: isFile ? book.path : '', // Placeholder for folder
          type: isFile ? 'file' : 'folder',
          children: isFile ? undefined : [],
          data: isFile ? book : undefined,
        }

        // For folders, unique path key needs to be accumulated
        if (!isFile) {
          const parentPath = parts.slice(0, i).join('/')
          newNode.path = parentPath ? `${parentPath}/${part}` : part || ''
        }

        currentLevel.push(newNode)

        // Sort: Folders first, then files. Alphabetical.
        currentLevel.sort((a, b) => {
          if (a.type !== b.type) {
            return a.type === 'folder' ? -1 : 1
          }
          return a.name.localeCompare(b.name)
        })

        if (!isFile) {
          currentLevel = newNode.children!
        }
      }
    }
  }
  nodes.value = root
}

function onNodeSelect(node: TreeNode) {
  if (node.type === 'file' && node.data) {
    router.push(`/reader/${node.data.id}`)
  }
}
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col h-full">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2 flex-shrink-0">
      <FolderIcon class="w-5 h-5 text-gray-500" />
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        文件目录
      </h2>
      <span class="text-xs text-gray-400 ml-auto">
        共 {{ booksStore.books.length }} 本书
      </span>
    </div>

    <div class="p-2 flex-1 overflow-y-auto min-h-0">
      <div v-if="nodes.length === 0" class="text-center py-12 text-gray-400 text-sm">
        书库为空，请先扫描
      </div>
      <TreeItem
        v-for="node in nodes"
        :key="node.path"
        :node="node"
        @select="onNodeSelect"
      />
    </div>
  </div>
</template>
