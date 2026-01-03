<script setup lang="ts">
import type { Chapter } from '@/types/api'

defineProps<{
  chapters: Chapter[]
  currentChapterIndex: number | null
  hasBook: boolean
}>()

const emit = defineEmits<{
  jumpToChapter: [chapterIndex: number]
}>()
</script>

<template>
  <Transition name="slide-down">
    <div v-if="true" data-toc-panel class="reader-toc" @click.stop>
      <div class="px-4 py-3">
        <h2 class="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-50">
          目录
        </h2>
        <div class="space-y-1">
          <button
            v-for="chapter in chapters" :key="chapter.id" class="w-full text-left px-3 py-2 rounded-lg transition-colors" :class="[
              currentChapterIndex === chapter.order_index
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300',
            ]"
            @click="emit('jumpToChapter', chapter.order_index)"
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
  /* Positioning handled by parent */
  width: 100%;
  height: 100%;
  overflow-y: auto;
}
</style>
