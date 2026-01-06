import type { Book, Chapter } from '@/types/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as api from '@/api'
import { useBooksStore } from './books'

export const useReaderStore = defineStore('reader', () => {
  const currentBook = ref<Book | null>(null)
  const chapters = ref<Chapter[]>([])
  const currentChapterIndex = ref<number | null>(null)
  const currentContent = ref<string>('')
  const loading = ref(false)
  const contentCache = ref<Map<number, string>>(new Map())

  // 当前章节
  const currentChapter = computed(() => {
    if (currentChapterIndex.value === null)
      return null
    return chapters.value.find(
      ch => ch.order_index === currentChapterIndex.value,
    ) || null
  })

  // 是否有上一章
  const hasPreviousChapter = computed(() => {
    if (currentChapterIndex.value === null)
      return false
    return currentChapterIndex.value > 0
  })

  // 是否有下一章
  const hasNextChapter = computed(() => {
    if (currentChapterIndex.value === null)
      return false
    return currentChapterIndex.value < chapters.value.length - 1
  })

  // 加载书籍和章节列表
  async function loadBook(bookId: number) {
    reset()

    loading.value = true
    try {
      currentBook.value = await api.getBook(bookId)
      chapters.value = await api.listChapters(bookId)

      // 恢复阅读位置
      if (currentBook.value && currentBook.value.chapter_index !== null) {
        currentChapterIndex.value = currentBook.value.chapter_index
        await loadChapter(currentBook.value.chapter_index)
      }
      else if (chapters.value.length > 0) {
        // 如果没有阅读记录，从第一章开始
        const firstChapter = chapters.value[0]
        if (firstChapter) {
          currentChapterIndex.value = firstChapter.order_index
          await loadChapter(currentChapterIndex.value)
        }
      }
    }
    catch (err) {
      console.error('Failed to load book:', err)
      throw err
    }
    finally {
      loading.value = false
    }
  }

  // 加载章节内容
  async function loadChapter(chapterIndex: number) {
    if (!currentBook.value)
      return

    // Check cache first
    if (contentCache.value.has(chapterIndex)) {
      currentContent.value = contentCache.value.get(chapterIndex)!
      currentChapterIndex.value = chapterIndex
      // Preload neighbors even if cache hit
      preloadNeighbors(chapterIndex)
      return
    }

    loading.value = true
    try {
      const content = await api.getChapterContent(
        currentBook.value.id!,
        chapterIndex,
      )
      currentContent.value = content
      contentCache.value.set(chapterIndex, content)
      currentChapterIndex.value = chapterIndex

      // Preload neighbors
      preloadNeighbors(chapterIndex)
    }
    catch (err) {
      console.error('Failed to load chapter:', err)
      throw err
    }
    finally {
      loading.value = false
    }
  }

  function preloadNeighbors(currentIndex: number) {
    if (!currentBook.value)
      return

    const bookId = currentBook.value.id!
    const targets = [
      currentIndex - 1, // Prev
      currentIndex + 1, // Next 1
      currentIndex + 2, // Next 2
    ]

    targets.forEach((index) => {
      // Validate index range
      if (index >= 0 && index < chapters.value.length) {
        // If not in cache, fetch it
        if (!contentCache.value.has(index)) {
          api.getChapterContent(bookId, index)
            .then((content) => {
              contentCache.value.set(index, content)
            })
            .catch(() => {
              // Ignore preload errors
            })
        }
      }
    })

    // Prune cache if it gets too big (> 20)
    if (contentCache.value.size > 20) {
      for (const key of contentCache.value.keys()) {
        if (Math.abs(key - currentIndex) > 10) {
          contentCache.value.delete(key)
        }
      }
    }
  }

  // 上一章
  async function previousChapter() {
    if (!hasPreviousChapter.value || !currentBook.value)
      return

    const prevIndex = currentChapterIndex.value! - 1
    await loadChapter(prevIndex)
  }

  // 下一章
  async function nextChapter() {
    if (!hasNextChapter.value || !currentBook.value)
      return

    const nextIndex = currentChapterIndex.value! + 1
    await loadChapter(nextIndex)
  }

  // 保存进度
  async function saveProgress(offset: number) {
    if (!currentBook.value || currentChapterIndex.value === null)
      return

    const booksStore = useBooksStore()
    await booksStore.updateProgress(
      currentBook.value.id!,
      currentChapterIndex.value,
      offset,
    )
  }

  // 标记已读完
  async function markFinished(finished: boolean) {
    if (!currentBook.value)
      return
    const updatedBook = await api.markFinished(currentBook.value.id!, finished)
    currentBook.value = updatedBook
  }

  // 重置状态
  function reset() {
    currentBook.value = null
    chapters.value = []
    currentChapterIndex.value = null
    currentContent.value = ''
    contentCache.value.clear()
  }

  return {
    currentBook,
    chapters,
    currentChapterIndex,
    currentContent,
    loading,
    currentChapter,
    hasPreviousChapter,
    hasNextChapter,
    loadBook,
    loadChapter,
    previousChapter,
    nextChapter,
    saveProgress,
    markFinished,
    reset,
  }
})
