/**
 * 书籍相关 API
 */

import { apiClient } from './client'
import type {
    Book,
    ListBooksParams,
    RandomBooksParams,
    UpdateProgressParams,
} from '../types/api'

/**
 * 获取书架列表
 */
export async function listBooks(params?: ListBooksParams): Promise<Book[]> {
    const searchParams = new URLSearchParams()
    if (params?.starred !== undefined) {
        searchParams.append('starred', String(params.starred))
    }
    if (params?.search) {
        searchParams.append('search', params.search)
    }
    if (params?.finished !== undefined) {
        searchParams.append('finished', String(params.finished))
    }

    return apiClient.get('books', { searchParams }).json<Book[]>()
}

/**
 * 随机获取书籍
 */
export async function getRandomBooks(
    params?: RandomBooksParams
): Promise<Book[]> {
    const searchParams = new URLSearchParams()
    if (params?.count) {
        searchParams.append('count', String(params.count))
    }

    return apiClient.get('books/random', { searchParams }).json<Book[]>()
}

/**
 * 获取书籍详情
 */
export async function getBook(bookId: number): Promise<Book> {
    return apiClient.get(`books/${bookId}`).json<Book>()
}

/**
 * 同步阅读进度
 */
export async function updateProgress(
    bookId: number,
    params: UpdateProgressParams
): Promise<Book> {
    return apiClient
        .patch(`books/${bookId}/progress`, {
            json: params,
        })
        .json<Book>()
}

/**
 * 手动标记为已读完/未读完
 */
export async function markFinished(
    bookId: number,
    finished: boolean
): Promise<Book> {
    return apiClient
        .patch(`books/${bookId}/finish`, {
            json: { finished },
        })
        .json<Book>()
}

/**
 * 标星/取消标星
 */
export async function toggleStar(
    bookId: number,
    starred: boolean
): Promise<Book> {
    return apiClient
        .patch(`books/${bookId}/star`, {
            json: { starred },
        })
        .json<Book>()
}

/**
 * 重新解析指定书籍
 */
export async function reparseBook(bookId: number): Promise<Book> {
    return apiClient.post(`books/${bookId}/reparse`).json<Book>()
}

/**
 * 从物理磁盘删除文件
 */
export async function deleteBook(bookId: number): Promise<{ message: string }> {
    return apiClient.delete(`books/${bookId}`).json<{ message: string }>()
}

