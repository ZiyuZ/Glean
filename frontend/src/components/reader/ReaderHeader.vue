<script setup lang="ts">
import { ArrowLeft, List } from 'lucide-vue-next'

defineProps<{
  title: string
  showTOC?: boolean
}>()

const emit = defineEmits<{
  back: []
  toggleTOC: []
}>()
</script>

<template>
  <Transition name="slide-down">
    <header
      class="reader-header"
    >
      <div class="flex items-center justify-between">
        <button
          @click.stop="emit('back')"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <ArrowLeft :size="20" />
          <span>返回</span>
        </button>
        <h1 class="text-lg font-semibold truncate flex-1 mx-4">
          {{ title || '加载中...' }}
        </h1>
        <button
          @click.stop="emit('toggleTOC')"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <List :size="20" />
        </button>
      </div>
    </header>
  </Transition>
</template>

<style scoped>
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgb(229, 231, 235);
  padding: 0.75rem 1rem;
}

.dark .reader-header {
  background-color: rgba(17, 24, 39, 0.95);
  border-bottom-color: rgb(31, 41, 55);
}
</style>

