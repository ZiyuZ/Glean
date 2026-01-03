<script setup lang="ts">
import { computed } from 'vue'
import { useReaderConfig } from '@/composables/useReader'

const props = defineProps<{
  content: string
  chapterTitle?: string
  currentPage: number
  totalPages: number
  showSettings: boolean
}>()

const { fontSize, lineHeight, padding, margin } = useReaderConfig()

const contentStyle = computed(() => ({
  fontSize: `${fontSize.value}px`,
  lineHeight: lineHeight.value,
  '--paragraph-margin': `${margin.value}px`,
}))

const containerStyle = computed(() => ({
  padding: `${padding.value / 2}px ${padding.value / 4}px`,
}))

// 将内容按段落分割
const contentParagraphs = computed(() => {
  const marker = '<NO_INDENT>'
  return props.content
    .split('\n\n')
    .filter((p) => p.trim())
    .map((p) => {
      const noIndent = p.startsWith(marker)
      const text = noIndent ? p.slice(marker.length) : p
      return { text, noIndent }
    })
})
</script>

<template>
  <div class="flex-1 flex flex-col">
    <!-- Chapter Title (only on first page) -->
    <h2 v-if="currentPage === 0 && chapterTitle" class="text-2xl font-bold mb-6 text-center px-6 pt-8">
      {{ chapterTitle }}
    </h2>

    <!-- Page Content -->
    <div
      class="flex-1 max-w-3xl mx-auto w-full overflow-hidden"
      :style="containerStyle"
    >
      <div 
        class="reader-content-text"
        :style="contentStyle"
      >
        <p 
          v-for="(paragraph, index) in contentParagraphs" 
          :key="index"
          class="reader-paragraph"
          :class="{ 'no-indent': paragraph.noIndent }"
        >
          {{ paragraph.text }}
        </p>
      </div>
    </div>

    <!-- Page Indicator -->
    <div
      v-if="!showSettings && totalPages > 1"
      class="reader-page-indicator"
    >
      {{ currentPage + 1 }} / {{ totalPages }}
    </div>
  </div>
</template>

<style scoped>
.reader-content-text {
  white-space: pre-wrap;
  height: 100%;
  word-break: break-word;
  text-align: justify;
  letter-spacing: 0.5px;
  overflow: hidden;
}

.reader-paragraph {
  margin-bottom: var(--paragraph-margin, 16px);
  text-indent: 2em; /* 段首缩进两个字符 */
}

.reader-paragraph.no-indent {
  text-indent: 0;
}

.reader-page-indicator {
  position: fixed;
  right: 0.25rem;
  top: 0.25rem;
  font-size: 0.875rem;
  color: rgb(107, 114, 128);
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  z-index: 5;
  pointer-events: none;
}

.dark .reader-page-indicator {
  color: rgb(156, 163, 175);
  background-color: rgba(31, 41, 55, 0.8);
}
</style>

