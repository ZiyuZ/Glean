/**
 * API 类型定义
 * 对应后端的 SQLModel 和 Pydantic 模型
 */

/**
 * 书籍模型
 */
export interface Book {
  id: number
  hash_id: string
  title: string
  path: string
  is_starred: boolean
  last_read_time: number | null
  file_size: number
  file_mtime: number
  chapter_index: number | null
  chapter_offset: number | null
  is_finished: boolean
  chapters?: Chapter[] // 关联章节（可选，某些 API 可能不包含）
}

/**
 * 章节模型
 */
export interface Chapter {
  id: number
  book_id: number
  title: string
  order_index: number
  content: string
}

/**
 * 扫描响应
 */
export interface ScanResponse {
  message: string
  files_scanned: number
  files_added: number
  files_updated: number
}

/**
 * 扫描状态响应
 */
export interface ScanStatusResponse {
  is_running: boolean
  files_scanned: number
  files_added: number
  files_updated: number
  total_files: number
  current_file: string
  error: string | null
}

/**
 * 停止扫描响应
 */
export interface StopScanResponse {
  message: string
}

/**
 * 更新进度请求参数
 */
export interface UpdateProgressParams {
  chapter_index: number
  chapter_offset: number
}

/**
 * 列表查询参数
 */
export interface ListBooksParams {
  starred?: boolean
  search?: string
  finished?: boolean
  started?: boolean
}

/**
 * 随机书籍查询参数
 */
export interface RandomBooksParams {
  count?: number // 1-100，默认 1
}
