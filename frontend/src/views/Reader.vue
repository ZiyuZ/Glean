<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useReaderStore } from '@/stores/reader'
import { useBooksStore } from '@/stores/books'
import { useReaderConfig } from '@/composables/useReader'
import { useDebounceFn } from '@vueuse/core'
import ReaderHeader from '@/components/reader/ReaderHeader.vue'
import ReaderTOC from '@/components/reader/ReaderTOC.vue'
import ReaderSettings from '@/components/reader/ReaderSettings.vue'
import ReaderContent from '@/components/reader/ReaderContent.vue'

const route = useRoute()
const router = useRouter()
const readerStore = useReaderStore()
const booksStore = useBooksStore()
const { fontSize, lineHeight, theme, brightness, padding, margin } = useReaderConfig()

// 容器引用
const containerRef = ref<HTMLElement | null>(null)
const showSettings = ref(false)
const showTOC = ref(false)

// 分页相关
const currentPage = ref(0)
const pages = ref<string[]>([])

// 触摸相关
const touchStart = ref<{ x: number; y: number } | null>(null)

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

// 当前页内容
const currentPageContent = computed(() => pages.value[currentPage.value] || '')

// 格式化内容（移除多余空白）
const formattedContent = computed(() => {
  if (!readerStore.currentContent) return ''
  return readerStore.currentContent
    .replace(/\r\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
})

// 分页函数：离屏测量，按容器高度切分文本
async function paginateContent(content: string) {
  if (!content || !containerRef.value) {
    pages.value = []
    currentPage.value = 0
    return
  }

  const container = containerRef.value
  const rect = container.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) return

  // 离屏测量容器
  const measure = document.createElement('div')
  measure.style.position = 'absolute'
  measure.style.left = '-9999px'
  measure.style.top = '-9999px'
  measure.style.visibility = 'hidden'
  measure.style.boxSizing = 'border-box'
  measure.style.width = `${Math.min(rect.width, 768)}px`
  measure.style.padding = `${padding.value / 2}px ${padding.value / 4}px`
  measure.style.fontSize = `${fontSize.value}px`
  measure.style.lineHeight = `${lineHeight.value}`
  measure.style.whiteSpace = 'pre-wrap'
  measure.style.wordBreak = 'break-word'
  measure.style.textAlign = 'justify'
  measure.style.letterSpacing = '0.5px'
  document.body.appendChild(measure)

  const pageList: string[] = []
  const paragraphs = content.split('\n\n').filter((p) => p.trim())
  let idx = 0
  let isFirstPage = true

  try {
    while (idx < paragraphs.length) {
      measure.innerHTML = ''
      let usedHeight = 0

      // 首页加标题高度，使用与 ReaderContent 相同的样式
      if (isFirstPage && readerStore.currentChapter?.title) {
        const titleEl = document.createElement('h2')
        titleEl.textContent = readerStore.currentChapter.title
        titleEl.style.fontSize = '24px' // tailwind text-2xl
        titleEl.style.fontWeight = '700'
        titleEl.style.padding = '32px 24px 0 24px' // pt-8 px-6
        titleEl.style.textAlign = 'center'
        titleEl.style.wordBreak = 'break-word'
        titleEl.style.margin = '0'
        titleEl.style.lineHeight = '1.2'
        measure.appendChild(titleEl)
        const h2h = titleEl.scrollHeight
        usedHeight += h2h + 24 /* mb-6 */
      }

      const availableHeight = rect.height - usedHeight
      if (availableHeight <= 0) break

      const pageParas: string[] = []

      while (idx < paragraphs.length) {
        const para = paragraphs[idx] ?? ''
        if (!para) {
          idx++
          continue
        }

        const p = document.createElement('p')
        p.style.marginBottom = `${margin.value}px`
        p.style.textIndent = '2em'
        p.textContent = para
        measure.appendChild(p)

        const h = p.scrollHeight
        const totalWithMargin = usedHeight + h + margin.value
        const totalNoMargin = usedHeight + h

        if (totalWithMargin > availableHeight && totalNoMargin > availableHeight) {
          // 二分查找最多可容纳的字符数
          let low = 0
          let high = para.length
          let best = 0
          while (low <= high) {
            const mid = Math.floor((low + high) / 2)
            p.textContent = para.slice(0, mid)
            const th = p.scrollHeight
            if (usedHeight + th <= availableHeight) {
              best = mid
              low = mid + 1
            } else {
              high = mid - 1
            }
          }

          if (best > 0) {
            const head = para.slice(0, best)
            const tail = para.slice(best)
            pageParas.push(head)
            paragraphs[idx] = `<NO_INDENT>${tail}`
          }
          break
        }

        pageParas.push(para)
        usedHeight += h
        // 若仍有段落且空间允许，加上段间距；若空间紧张则省略间距以多放文字
        if (idx < paragraphs.length - 1 && usedHeight + margin.value <= availableHeight) {
          usedHeight += margin.value
        }
        idx++
      }

      if (pageParas.length === 0 && idx < paragraphs.length) {
        // 极端情况至少放一个字符
        const para = paragraphs[idx] ?? ''
        if (para.length > 0) {
          pageParas.push(para.slice(0, 1))
          paragraphs[idx] = para.slice(1)
        }
      }

      const text = pageParas.join('\n\n').trim()
      if (text) pageList.push(text)
      isFirstPage = false
    }

    pages.value = pageList
    if (currentPage.value >= pages.value.length && pages.value.length > 0) {
      currentPage.value = pages.value.length - 1
    }
  } finally {
    document.body.removeChild(measure)
  }
}

// 计算当前偏移量
function calculateCurrentOffset(): number {
  if (!readerStore.currentContent || pages.value.length === 0) return 0
  let offset = 0
  for (let i = 0; i <= currentPage.value && i < pages.value.length; i++) {
    offset += pages.value[i]?.length || 0
  }
  return Math.min(offset, readerStore.currentContent.length)
}

// 保存进度
async function saveProgressNow() {
  if (!readerStore.currentBook || readerStore.currentChapterIndex === null) return
  const offset = calculateCurrentOffset()
  await readerStore.saveProgress(offset)
  await booksStore.fetchBooks()
}

const saveProgressDebounced = useDebounceFn(saveProgressNow, 2000)

// 上一页
function previousPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    saveProgressDebounced()
  } else if (readerStore.hasPreviousChapter) {
    saveProgressNow().then(async () => {
      await readerStore.previousChapter()
      await paginateContent(formattedContent.value)
      currentPage.value = pages.value.length - 1
    })
  }
}

// 下一页
function nextPage() {
  if (currentPage.value < pages.value.length - 1) {
    currentPage.value++
    saveProgressDebounced()
  } else if (readerStore.hasNextChapter) {
    saveProgressNow().then(async () => {
      await readerStore.nextChapter()
      await paginateContent(formattedContent.value)
      currentPage.value = 0
    })
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
  if (!rect) return

  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const col = Math.floor((x / rect.width) * 3)
  const row = Math.floor((y / rect.height) * 3)

  if (col === 0 || row === 0) {
    previousPage()
  } else if (col === 1 && row === 1) {
    showSettings.value = true
  } else {
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
  if (!touchStart.value) return
  const touch = event.changedTouches[0]
  if (!touch) return

  const dx = touch.clientX - touchStart.value.x
  const dy = touch.clientY - touchStart.value.y
  const threshold = 50

  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > threshold) {
    if (dx > 0) {
      previousPage()
    } else {
      nextPage()
    }
  } else if (Math.abs(dy) > threshold) {
    if (dy > 0) {
      previousPage()
    } else {
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
    await paginateContent(formattedContent.value)
    currentPage.value = 0
  })
}

// 加载书籍
onMounted(async () => {
  const bookId = parseInt(route.params.bookId as string)
  if (isNaN(bookId)) {
    router.push('/')
    return
  }

  try {
    await readerStore.loadBook(bookId)
    await nextTick()
    if (formattedContent.value) {
      await paginateContent(formattedContent.value)
    }

    // 如果首次分页为空，重试一次
    if (pages.value.length === 0 && formattedContent.value) {
      await nextTick()
      await paginateContent(formattedContent.value)
    }

    // 恢复阅读位置
    const offset = readerStore.currentBook?.chapter_offset
    if (offset != null && pages.value.length > 0) {
      let accumulated = 0
      for (let i = 0; i < pages.value.length; i++) {
        accumulated += pages.value[i]?.length || 0
        if (accumulated >= offset) {
          currentPage.value = i
          break
        }
      }
    }
  } catch (err) {
    console.error('Failed to load book:', err)
    router.push('/')
  }
})

// 监听内容变化，重新分页
watch([formattedContent, fontSize, lineHeight, padding, margin], async () => {
  if (formattedContent.value) {
    await nextTick()
    await paginateContent(formattedContent.value)
  }
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
    ref="containerRef"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
    @click="handleClick"
    :class="[
      'fixed inset-0 overflow-hidden',
      themeStyles.bg,
      themeStyles.text,
    ]"
    :style="{
      filter: `brightness(${brightness}%)`,
    }"
    class="reader-container"
  >
    <!-- Header -->
    <ReaderHeader
      v-if="showSettings || showTOC || !readerStore.currentBook"
      :title="readerStore.currentBook?.title || ''"
      :show-t-o-c="showTOC"
      @back="saveProgressNow().then(() => router.back())"
      @toggle-t-o-c="showTOC = !showTOC"
    />

    <!-- TOC Panel -->
    <ReaderTOC
      v-if="showTOC"
      :chapters="readerStore.chapters"
      :current-chapter-index="readerStore.currentChapterIndex"
      :show-settings="showSettings"
      :has-book="!!readerStore.currentBook"
      @jump-to-chapter="jumpToChapter"
    />

    <!-- Settings Panel -->
    <ReaderSettings v-if="showSettings" />

    <!-- Content -->
    <main class="h-full overflow-hidden flex flex-col">
      <div v-if="readerStore.loading" class="flex-1 flex items-center justify-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-current"></div>
      </div>

      <ReaderContent
        v-else-if="readerStore.currentChapter"
        :content="currentPageContent"
        :chapter-title="readerStore.currentChapter.title"
        :current-page="currentPage"
        :total-pages="pages.length"
        :show-settings="showSettings"
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
