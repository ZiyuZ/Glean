<script setup lang="ts">
import type { Chapter } from '@/types/api'

defineProps<{
  chapters: Chapter[]
  currentChapterIndex: number | null
  showSettings: boolean
  hasBook: boolean
}>()

const emit = defineEmits<{
  jumpToChapter: [chapterIndex: number]
}>()
</script>

<template>
  <Transition name="slide-down">
    <div
      v-if="true"
      data-toc-panel
      @click.stop
      class="reader-toc"
      :class="{ 'reader-toc--with-header': showSettings || !hasBook }"
    >
      <div class="px-4 py-3">
        <h2 class="text-lg font-semibold mb-3">目录</h2>
        <div class="space-y-1">
          <button
            v-for="chapter in chapters"
            :key="chapter.id"
            @click="emit('jumpToChapter', chapter.order_index)"
            :class="[
              'w-full text-left px-3 py-2 rounded-lg transition-colors',
              currentChapterIndex === chapter.order_index
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
            ]"
          >
            {{ chapter.title }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.reader-toc {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  z-index: 30;
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgb(229, 231, 235);
  max-height: 80vh;
  overflow-y: auto;
}

.dark .reader-toc {
  background-color: rgba(17, 24, 39, 0.95);
  border-bottom-color: rgb(31, 41, 55);
}

.reader-toc--with-header {
  margin-top: 60px;
}
</style>

