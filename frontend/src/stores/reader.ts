import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Book, Chapter } from '@/types/api'
import * as api from '@/api'
import { useBooksStore } from './books'

export const useReaderStore = defineStore('reader', () => {
  const currentBook = ref<Book | null>(null)
  const chapters = ref<Chapter[]>([])
  const currentChapterIndex = ref<number | null>(null)
  const currentContent = ref<string>('')
  const loading = ref(false)

  // 当前章节
  const currentChapter = computed(() => {
    if (currentChapterIndex.value === null) return null
    return chapters.value.find(
      (ch) => ch.order_index === currentChapterIndex.value
    ) || null
  })

  // 是否有上一章
  const hasPreviousChapter = computed(() => {
    if (currentChapterIndex.value === null) return false
    return currentChapterIndex.value > 0
  })

  // 是否有下一章
  const hasNextChapter = computed(() => {
    if (currentChapterIndex.value === null) return false
    return currentChapterIndex.value < chapters.value.length - 1
  })

  // 加载书籍和章节列表
  async function loadBook(bookId: number) {
    loading.value = true
    try {
      currentBook.value = await api.getBook(bookId)
      chapters.value = await api.listChapters(bookId)

      // 恢复阅读位置
      if (currentBook.value.chapter_index !== null) {
        currentChapterIndex.value = currentBook.value.chapter_index
        await loadChapter(currentBook.value.chapter_index)
      } else if (chapters.value.length > 0) {
        // 如果没有阅读记录，从第一章开始
        currentChapterIndex.value = chapters.value[0].order_index
        await loadChapter(currentChapterIndex.value)
      }
    } catch (err) {
      console.error('Failed to load book:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 加载章节内容
  async function loadChapter(chapterIndex: number) {
    if (!currentBook.value) return

    loading.value = true
    try {
      currentContent.value = await api.getChapterContent(
        currentBook.value.id!,
        chapterIndex
      )
      currentChapterIndex.value = chapterIndex

      // 预加载下一章
      if (hasNextChapter.value) {
        const nextIndex = chapterIndex + 1
        api.getChapterContent(currentBook.value.id!, nextIndex).catch(() => {
          // 静默失败
        })
      }
    } catch (err) {
      console.error('Failed to load chapter:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 上一章
  async function previousChapter() {
    if (!hasPreviousChapter.value || !currentBook.value) return

    const prevIndex = currentChapterIndex.value! - 1
    await loadChapter(prevIndex)
  }

  // 下一章
  async function nextChapter() {
    if (!hasNextChapter.value || !currentBook.value) return

    const nextIndex = currentChapterIndex.value! + 1
    await loadChapter(nextIndex)
  }

  // 保存进度
  async function saveProgress(offset: number) {
    if (!currentBook.value || currentChapterIndex.value === null) return

    const booksStore = useBooksStore()
    await booksStore.updateProgress(
      currentBook.value.id!,
      currentChapterIndex.value,
      offset
    )
  }

  // 重置状态
  function reset() {
    currentBook.value = null
    chapters.value = []
    currentChapterIndex.value = null
    currentContent.value = ''
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
    reset,
  }
})

