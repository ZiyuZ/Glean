<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import ReaderContent from '@/components/reader/ReaderContent.vue'
import ReaderHeader from '@/components/reader/ReaderHeader.vue'
import ReaderSettings from '@/components/reader/ReaderSettings.vue'
import ReaderTOC from '@/components/reader/ReaderTOC.vue'
import { useReaderConfig } from '@/composables/useReader'
import { useBooksStore } from '@/stores/books'
import { useReaderStore } from '@/stores/reader'

const route = useRoute()
const router = useRouter()
const readerStore = useReaderStore()
const booksStore = useBooksStore()
const { fontSize, lineHeight, theme, brightness, padding, margin } = useReaderConfig()

// 容器引用
const containerRef = ref<HTMLElement | null>(null)
const showSettings = ref(false)
const showTOC = ref(false)

// 分页/滚动相关（列布局）
const currentPage = ref(0)
const totalPages = ref(1)
const contentRef = ref<InstanceType<typeof ReaderContent> | null>(null)
const columnWidth = ref<number>(0)
const columnGap = ref<number>(0)

// 触摸相关
const touchStart = ref<{ x: number, y: number } | null>(null)

// 主题样式
const themeStyles = computed(() => {
  const themes = {
    light: { bg: 'bg-white', text: 'text-gray-900' },
    sepia: { bg: 'bg-amber-50', text: 'text-amber-900' },
    dark: { bg: 'bg-gray-800', text: 'text-gray-100' },
    night: { bg: 'bg-black', text: 'text-gray-300' },
  }
  return themes[theme.value]
})

// 格式化内容（移除多余空白）
const formattedContent = computed(() => {
  if (!readerStore.currentContent)
    return ''
  return readerStore.currentContent
    .replace(/\r\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
})

function getScrollEl(): HTMLElement | null {
  return contentRef.value?.scrollEl ?? null
}

function updateColumnsSize() {
  const rect = containerRef.value?.getBoundingClientRect()
  if (!rect)
    return
  // 列宽约等于可视宽度（保持与屏幕宽度一致），留出少量 gap
  columnWidth.value = Math.max(1, rect.width)
  columnGap.value = 0
}

function updatePages() {
  const el = getScrollEl()
  if (!el)
    return
  const pageW = el.clientWidth || 1
  const total = Math.max(1, Math.ceil(el.scrollWidth / pageW))
  totalPages.value = total
}

function syncCurrentPage() {
  const el = getScrollEl()
  if (!el)
    return
  const pageW = el.clientWidth || 1
  const page = Math.round(el.scrollLeft / pageW)
  currentPage.value = Math.min(Math.max(page, 0), totalPages.value - 1)
}

async function recalcPagination() {
  await nextTick()
  updateColumnsSize()
  await nextTick()
  updatePages()
  syncCurrentPage()
}

function goToPage(page: number) {
  const el = getScrollEl()
  if (!el)
    return
  const pageW = el.clientWidth || 1
  const clamped = Math.min(Math.max(page, 0), totalPages.value - 1)
  el.scrollTo({ left: clamped * pageW, behavior: 'smooth' })
}

// 计算当前偏移量（按滚动比例近似）
function calculateCurrentOffset(): number {
  if (!readerStore.currentContent)
    return 0
  const el = getScrollEl()
  if (!el || el.scrollWidth <= el.clientWidth)
    return 0
  const ratio = el.scrollLeft / (el.scrollWidth - el.clientWidth)
  return Math.min(
    Math.floor(ratio * readerStore.currentContent.length),
    readerStore.currentContent.length,
  )
}

// 保存进度
async function saveProgressNow() {
  if (!readerStore.currentBook || readerStore.currentChapterIndex === null)
    return
  const offset = calculateCurrentOffset()
  await readerStore.saveProgress(offset)
  await booksStore.fetchBooks()
}

const saveProgressDebounced = useDebounceFn(saveProgressNow, 2000)

// 上一页
async function previousPage() {
  await recalcPagination()
  if (currentPage.value > 0) {
    goToPage(currentPage.value - 1)
    saveProgressDebounced()
  }
  else if (readerStore.hasPreviousChapter) {
    await saveProgressNow()
    await readerStore.previousChapter()
    await recalcPagination()
    goToPage(totalPages.value - 1)
  }
}

// 下一页
async function nextPage() {
  await recalcPagination()
  if (currentPage.value < totalPages.value - 1) {
    goToPage(currentPage.value + 1)
    saveProgressDebounced()
  }
  else if (readerStore.hasNextChapter) {
    await saveProgressNow()
    await readerStore.nextChapter()
    await recalcPagination()
    goToPage(0)
  }
}

// 点击处理
function handleClick(event: MouseEvent) {
  if (showSettings.value || showTOC.value) {
    const target = event.target as HTMLElement
    if (!target.closest('[data-settings-panel]') && !target.closest('[data-toc-panel]')) {
      showSettings.value = false
      showTOC.value = false
    }
    return
  }

  const rect = containerRef.value?.getBoundingClientRect()
  if (!rect)
    return

  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const col = Math.floor((x / rect.width) * 3)
  const row = Math.floor((y / rect.height) * 3)

  if (col === 0 || row === 0) {
    previousPage()
  }
  else if (col === 1 && row === 1) {
    showSettings.value = true
  }
  else {
    nextPage()
  }
}

// 触摸处理
function handleTouchStart(event: TouchEvent) {
  const touch = event.touches[0]
  if (touch) {
    touchStart.value = { x: touch.clientX, y: touch.clientY }
  }
}

function handleTouchEnd(event: TouchEvent) {
  if (!touchStart.value)
    return
  const touch = event.changedTouches[0]
  if (!touch)
    return

  const dx = touch.clientX - touchStart.value.x
  const dy = touch.clientY - touchStart.value.y
  const threshold = 50

  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > threshold) {
    if (dx > 0) {
      previousPage()
    }
    else {
      nextPage()
    }
  }
  else if (Math.abs(dy) > threshold) {
    if (dy > 0) {
      previousPage()
    }
    else {
      nextPage()
    }
  }

  touchStart.value = null
}

// 跳转到章节
function jumpToChapter(chapterIndex: number) {
  showTOC.value = false
  saveProgressNow().then(async () => {
    await readerStore.loadChapter(chapterIndex)
    await nextTick()
    updateColumnsSize()
    await nextTick()
    updatePages()
    goToPage(0)
  })
}

// 加载书籍
onMounted(async () => {
  const bookId = Number.parseInt(route.params.bookId as string)
  if (Number.isNaN(bookId)) {
    router.push('/')
    return
  }

  try {
    await readerStore.loadBook(bookId)
    await recalcPagination()

    // 恢复阅读位置（按字符偏移比例近似）
    const offset = readerStore.currentBook?.chapter_offset
    if (offset != null && readerStore.currentContent?.length) {
      const ratio = offset / readerStore.currentContent.length
      const el = getScrollEl()
      if (el && el.scrollWidth > el.clientWidth) {
        const target = ratio * (el.scrollWidth - el.clientWidth)
        el.scrollLeft = target
        await recalcPagination()
      }
    }
  }
  catch (err) {
    console.error('Failed to load book:', err)
    router.push('/')
  }
})

// 监听内容变化，重新分页
watch([formattedContent, fontSize, lineHeight, padding, margin], async () => {
  await recalcPagination()
})

// 离开前保存
onBeforeRouteLeave(async () => {
  await saveProgressNow()
})

onBeforeUnmount(async () => {
  await saveProgressNow()
  readerStore.reset()
})
</script>

<template>
  <div
    ref="containerRef" :class="[
      themeStyles.bg,
      themeStyles.text,
    ]" :style="{
      filter: `brightness(${brightness}%)`,
    }" class="reader-container fixed inset-0 overflow-hidden" @touchstart="handleTouchStart" @touchend="handleTouchEnd" @click="handleClick"
  >
    <!-- Header -->
    <ReaderHeader
      v-if="showSettings || showTOC || !readerStore.currentBook"
      :title="readerStore.currentBook?.title || ''" :show-t-o-c="showTOC"
      @back="saveProgressNow().then(() => router.back())" @toggle-t-o-c="showTOC = !showTOC"
    />

    <!-- TOC Panel -->
    <ReaderTOC
      v-if="showTOC" :chapters="readerStore.chapters" :current-chapter-index="readerStore.currentChapterIndex"
      :show-settings="showSettings" :has-book="!!readerStore.currentBook" @jump-to-chapter="jumpToChapter"
    />

    <!-- Settings Panel -->
    <ReaderSettings v-if="showSettings" />

    <!-- Content -->
    <main class="h-full overflow-hidden flex flex-col">
      <div v-if="readerStore.loading" class="flex-1 flex items-center justify-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-current" />
      </div>

      <ReaderContent
        v-else-if="readerStore.currentChapter" ref="contentRef" :content="formattedContent"
        :chapter-title="readerStore.currentChapter.title" :current-page="currentPage" :total-pages="totalPages"
        :show-settings="showSettings" :column-width="columnWidth" :column-gap="columnGap" @scroll="syncCurrentPage()"
      />
    </main>
  </div>
</template>

<style scoped>
.reader-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
