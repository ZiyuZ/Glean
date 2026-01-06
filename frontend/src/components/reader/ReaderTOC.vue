<script setup lang="ts">
import type { Chapter } from '@/types/api'
import { ChevronDoubleDownIcon, ChevronDoubleUpIcon } from '@heroicons/vue/24/outline'
import { ref } from 'vue'

defineProps<{
  chapters: Chapter[]
  currentChapterIndex: number | null
  hasBook: boolean
}>()

const emit = defineEmits<{
  jumpToChapter: [chapterIndex: number]
}>()

const listRef = ref<HTMLElement | null>(null)

function scrollToTop() {
  listRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
}

function scrollToBottom() {
  if (listRef.value) {
    listRef.value.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-900 rounded-t-xl overflow-hidden">
    <!-- Sticky Header -->
    <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800 shrink-0">
      <h2 class="text-lg font-bold text-gray-900 dark:text-gray-50">
        目录
        <span class="ml-2 text-xs font-normal text-gray-400 dark:text-gray-500 tabular-nums">
          {{ chapters.length }} 章节
        </span>
      </h2>
      <div class="flex gap-1">
        <button
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 active:scale-95 transition-all text-gray-500 dark:text-gray-400"
          title="回到顶部"
          @click="scrollToTop"
        >
          <ChevronDoubleUpIcon class="w-5 h-5" />
        </button>
        <button
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 active:scale-95 transition-all text-gray-500 dark:text-gray-400"
          title="跳到底部"
          @click="scrollToBottom"
        >
          <ChevronDoubleDownIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Scrollable Chapter List -->
    <div ref="listRef" class="flex-1 overflow-y-auto overscroll-contain py-2 px-3 no-scrollbar">
      <div class="space-y-1">
        <button
          v-for="(chapter, index) in chapters"
          :key="chapter.id"
          class="w-full text-left px-4 py-3 rounded-xl transition-all flex items-center gap-3 group active:scale-[0.98]"
          :class="[
            currentChapterIndex === chapter.order_index
              ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-semibold'
              : 'hover:bg-gray-50 dark:hover:bg-gray-800/50 text-gray-700 dark:text-gray-300',
          ]"
          @click="emit('jumpToChapter', chapter.order_index)"
        >
          <span
            class="text-xs tabular-nums min-w-[1.5rem] opacity-40 group-hover:opacity-100 transition-opacity"
            :class="{ 'opacity-100': currentChapterIndex === chapter.order_index }"
          >
            {{ (index + 1).toString().padStart(2, '0') }}
          </span>
          <span class="truncate">{{ chapter.title }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
