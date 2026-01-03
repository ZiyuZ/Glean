/**
 * 章节相关 API
 */

import { apiClient } from './client'
import type { Chapter } from '../types/api'

/**
 * 获取书籍的章节目录
 */
export async function listChapters(bookId: number): Promise<Chapter[]> {
    return apiClient.get(`books/${bookId}/chapters`).json<Chapter[]>()
}

/**
 * 获取特定章节的纯文本内容
 * 
 * 注意：返回的是纯文本，不是 JSON
 */
export async function getChapterContent(
    bookId: number,
    chapterIndex: number
): Promise<string> {
    return apiClient.get(`books/${bookId}/chapters/${chapterIndex}`).text()
}

