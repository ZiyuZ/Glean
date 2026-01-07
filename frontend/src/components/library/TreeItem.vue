<script setup lang="ts">
import type { TreeNode } from './FileTree.vue'
import { CheckCircleIcon, ChevronRightIcon, ClockIcon, DocumentTextIcon, FolderIcon, FolderOpenIcon } from '@heroicons/vue/24/outline'
import { computed, ref } from 'vue'

const props = defineProps<{
  node: TreeNode
  level?: number
}>()

const emit = defineEmits<{
  (e: 'select', node: TreeNode): void
}>()

const isOpen = ref(false)
const currentLevel = computed(() => props.level ?? 0)

const displayName = computed(() => {
  if (props.node.type === 'file') {
    return props.node.name.replace(/\.txt$/i, '')
  }
  return props.node.name
})

function toggle() {
  if (props.node.type === 'folder') {
    isOpen.value = !isOpen.value
  }
}

function onClick() {
  if (props.node.type === 'folder') {
    toggle()
  }
  else {
    emit('select', props.node)
  }
}
</script>

<template>
  <div>
    <!-- Item Row -->
    <div
      class="flex items-center py-2 px-2 rounded-lg cursor-pointer transition-colors text-sm select-none"
      :class="[
        currentLevel === 0 ? 'hover:bg-gray-100 dark:hover:bg-gray-800' : 'hover:bg-gray-100 dark:hover:bg-gray-800',
        node.type === 'file' ? 'text-gray-700 dark:text-gray-200' : 'text-gray-900 dark:text-white font-medium',
      ]"
      :style="{ paddingLeft: `${currentLevel * 1.5 + 0.5}rem` }"
      @click="onClick"
    >
      <!-- Expander Arrow (only for folders) -->
      <span
        class="mr-1 w-4 h-4 flex-shrink-0 transition-transform duration-200"
        :class="[
          node.type === 'folder' ? (isOpen ? 'rotate-90 text-gray-400' : 'text-gray-400/70') : 'invisible',
        ]"
      >
        <ChevronRightIcon class="w-4 h-4" />
      </span>

      <!-- Icon -->
      <span class="mr-2 text-gray-500 dark:text-gray-400">
        <FolderOpenIcon v-if="node.type === 'folder' && isOpen" class="w-5 h-5 text-blue-500 dark:text-blue-400" />
        <FolderIcon v-else-if="node.type === 'folder'" class="w-5 h-5" />
        <DocumentTextIcon v-else class="w-5 h-5" />
      </span>

      <!-- Name -->
      <span class="truncate">{{ displayName }}</span>

      <!-- Meta info (for files) -->
      <span v-if="node.type === 'file' && node.data" class="ml-auto text-xs flex items-center gap-1">
        <span
          v-if="node.data.is_finished"
          title="已读完"
          class="text-green-500 dark:text-green-400"
        >
          <CheckCircleIcon class="w-4 h-4" />
        </span>
        <span
          v-else-if="node.data.chapter_index !== null"
          title="阅读中"
          class="text-blue-500 dark:text-blue-400"
        >
          <ClockIcon class="w-4 h-4" />
        </span>
      </span>
    </div>

    <!-- Children (Recursive) -->
    <div v-if="node.type === 'folder' && isOpen">
      <TreeItem
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :level="currentLevel + 1"
        @select="emit('select', $event)"
      />
    </div>
  </div>
</template>
