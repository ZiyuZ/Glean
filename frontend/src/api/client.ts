/**
 * API 客户端配置
 * 使用 ky 作为 HTTP 客户端
 */

import ky from 'ky'
import { toast } from 'vue-sonner'
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
    beforeRequest: [
      (request) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
    afterResponse: [
      async (request, _options, response) => {
        if (response.ok && request.method !== 'GET') {
          try {
            const data = await response.clone().json()
            if (data && typeof data.message === 'string') {
              toast.success(data.message)
            }
          }
          catch {
            // 忽略非 JSON 响应或解析错误
          }
        }
        return response
      },
    ],
    beforeError: [
      async (error) => {
        const { response } = error
        if (response) {
          if (response.status === 401) {
            // 派发未授权事件，由 App.vue 或 main.ts 统一处理跳转
            // 避免在非组件环境直接操作路由或强制刷新
            window.dispatchEvent(new CustomEvent('auth:unauthorized'))
          }

          if (response.body) {
            try {
              const body = await response.json<{ detail: string }>()
              // FastAPI 错误响应格式：{"detail": "error message"}
              if (body.detail) {
                error.message = body.detail
                toast.error(body.detail)
              }
            }
            catch {
              // 如果解析失败，使用默认错误消息
            }
          }
        }
        return error
      },
    ],
  },

})

/**
 * 将对象转换为 URLSearchParams，自动过滤 undefined 和 null
 */
export function toSearchParams(params: Record<string, any>): URLSearchParams {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value))
    }
  }
  return searchParams
}
