import type { Book } from '@/types/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as api from '@/api'

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 筛选条件
  const starredFilter = ref<boolean | undefined>(undefined)
  const finishedFilter = ref<boolean | undefined>(undefined)
  const searchQuery = ref('')

  // 筛选后的书籍列表（只显示有进度的书籍）
  const filteredBooks = computed(() => {
    // 只显示有阅读进度的书籍（chapter_index !== null）
    let result = books.value.filter(book => book.chapter_index !== null)

    if (starredFilter.value !== undefined) {
      result = result.filter(book => book.is_starred === starredFilter.value)
    }

    if (finishedFilter.value !== undefined) {
      result = result.filter(book => book.is_finished === finishedFilter.value)
    }

    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(book =>
        book.title.toLowerCase().includes(query),
      )
    }

    return result
  })

  // 获取书籍列表
  async function fetchBooks() {
    loading.value = true
    error.value = null
    try {
      books.value = await api.listBooks({
        starred: starredFilter.value,
        finished: finishedFilter.value,
        search: searchQuery.value || undefined,
      })
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '获取书籍列表失败'
      console.error('Failed to fetch books:', err)
    }
    finally {
      loading.value = false
    }
  }

  // 获取随机书籍
  async function fetchRandomBooks(count: number = 1) {
    loading.value = true
    error.value = null
    try {
      return await api.getRandomBooks({ count })
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '获取随机书籍失败'
      console.error('Failed to fetch random books:', err)
      return []
    }
    finally {
      loading.value = false
    }
  }

  // 更新阅读进度
  async function updateProgress(
    bookId: number,
    chapterIndex: number,
    chapterOffset: number,
  ) {
    try {
      const updatedBook = await api.updateProgress(bookId, {
        chapter_index: chapterIndex,
        chapter_offset: chapterOffset,
      })
      // 更新本地状态
      const index = books.value.findIndex(b => b.id === bookId)
      if (index !== -1) {
        books.value[index] = updatedBook
      }
    }
    catch (err) {
      console.error('Failed to update progress:', err)
    }
  }

  // 切换标星状态
  async function toggleStar(bookId: number, starred: boolean) {
    try {
      const updatedBook = await api.toggleStar(bookId, starred)
      const index = books.value.findIndex(b => b.id === bookId)
      if (index !== -1) {
        books.value[index] = updatedBook
      }
    }
    catch (err) {
      console.error('Failed to toggle star:', err)
    }
  }

  // 删除书籍
  async function deleteBook(bookId: number) {
    try {
      await api.deleteBook(bookId)
      books.value = books.value.filter(b => b.id !== bookId)
    }
    catch (err) {
      console.error('Failed to delete book:', err)
      throw err
    }
  }

  return {
    books,
    loading,
    error,
    starredFilter,
    finishedFilter,
    searchQuery,
    filteredBooks,
    fetchBooks,
    fetchRandomBooks,
    updateProgress,
    toggleStar,
    deleteBook,
  }
})
