/**
 * API 客户端配置
 * 使用 ky 作为 HTTP 客户端
 */

import ky from 'ky'

/**
 * 创建 API 客户端实例
 *
 * 配置：
 * - 基础 URL：根据环境自动判断（开发环境使用代理，生产环境使用相对路径）
 * - 前缀：/api
 * - 超时：30 秒
 * - 错误处理：统一处理 HTTP 错误
 */
export const apiClient = ky.create({
  prefixUrl: '/api',
  timeout: 30000,
  retry: {
    limit: 2,
    methods: ['get'],
    statusCodes: [408, 413, 429, 500, 502, 503, 504],
  },
  hooks: {
    beforeError: [
      async (error) => {
        const { response } = error
        if (response && response.body) {
          try {
            const body = await response.json<{ detail: string }>()
            // FastAPI 错误响应格式：{"detail": "error message"}
            if (body.detail) {
              error.message = body.detail
            }
          }
          catch {
            // 如果解析失败，使用默认错误消息
          }
        }
        return error
      },
    ],
  },
})
