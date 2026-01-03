<script setup lang="ts">
import { computed, ref } from 'vue'
import { useReaderConfig } from '@/composables/useReader'

const props = defineProps<{
  content: string
  chapterTitle?: string
  currentPage: number
  totalPages: number
  showSettings: boolean
  columnWidth: number
  columnGap: number
}>()

const emit = defineEmits<{
  scroll: [event: Event]
}>()

const { fontSize, lineHeight, padding, margin } = useReaderConfig()
const scrollEl = ref<HTMLElement | null>(null)
defineExpose({ scrollEl })

const contentStyle = computed(() => ({
  'fontSize': `${fontSize.value}px`,
  'lineHeight': lineHeight.value,
  '--paragraph-margin': `${margin.value}px`,
}))

const containerStyle = computed(() => ({
  padding: `${padding.value / 4}px ${padding.value / 4}px`,
  columnWidth: props.columnWidth ? `${props.columnWidth}px` : '100vw',
  columnGap: `${props.columnGap || 0}px`,
  height: '100%',
}))

// 将内容按段落分割
const contentParagraphs = computed(() => {
  const marker = '<NO_INDENT>'
  return props.content
    .split('\n\n')
    .filter(p => p.trim())
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
      ref="scrollEl" class="reader-columns flex-1 w-full h-full" :style="containerStyle"
      @scroll="emit('scroll', $event)"
    >
      <p
        v-for="(paragraph, index) in contentParagraphs" :key="index" class="reader-paragraph"
        :class="{ 'no-indent': paragraph.noIndent }" :style="contentStyle"
      >
        {{ paragraph.text }}
      </p>
    </div>

    <!-- Page Indicator -->
    <div v-if="!showSettings && totalPages > 1" class="reader-page-indicator">
      {{ currentPage + 1 }} / {{ totalPages }}
    </div>
  </div>
</template>

<style scoped>
.reader-columns {
  overflow-x: auto;
  overflow-y: hidden;
  white-space: normal;
  column-fill: auto;
  column-count: auto;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x mandatory;
  scroll-snap-stop: always;
  /* 让浏览器按列排版为横向分页 */
}

.reader-columns>* {
  break-inside: avoid;
  scroll-snap-align: start;
}

.reader-paragraph {
  margin-bottom: var(--paragraph-margin, 16px);
  text-indent: 2em;
  /* 段首缩进两个字符 */
  text-align: justify;
  letter-spacing: 0.5px;
}

.reader-paragraph.no-indent {
  text-indent: 0;
}

.reader-page-indicator {
  position: fixed;
  right: 0.15rem;
  top: 0.15rem;
  font-size: 0.75rem;
  color: rgb(107, 114, 128);
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.15rem 0.75rem;
  z-index: 5;
  pointer-events: none;
}

.dark .reader-page-indicator {
  color: rgb(156, 163, 175);
  background-color: rgba(31, 41, 55, 0.8);
}
</style>
