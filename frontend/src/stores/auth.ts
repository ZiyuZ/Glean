import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, checkAuthStatus } from '../api/system'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const isAuthEnabled = ref(false)
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))
  const isInitialized = ref(false)

  // 初始化：检查后端是否开启了验证
  async function init() {
    if (isInitialized.value)
      return

    try {
      const status = await checkAuthStatus()
      isAuthEnabled.value = status.enabled
      localStorage.setItem('auth_required', String(status.enabled))

      // 如果后端未启用验证，则前端视为始终已认证
      if (!status.enabled) {
        isAuthenticated.value = true
      }
      isInitialized.value = true
    }
    catch (e) {
      console.error('Failed to check auth status', e)
      // 离线模式下，尝试读取本地缓存的配置
      const cachedAuth = localStorage.getItem('auth_required')
      if (cachedAuth === 'true') {
        isAuthEnabled.value = true
      }
      isInitialized.value = true
    }
  }

  // 登录动作
  async function login(password: string) {
    try {
      const res = await apiLogin(password)
      if (res.access_token) {
        // 如果是真实 Token，存入本地
        if (res.access_token !== 'no-auth-needed') {
          localStorage.setItem('access_token', res.access_token)
        }
        isAuthenticated.value = true
        return true
      }
    }
    catch {
      // 登录失败
    }
    return false
  }

  // 登出
  function logout() {
    localStorage.removeItem('access_token')
    isAuthenticated.value = false
    // 路由跳转交由调用者处处理，避免 store 与 router 循环依赖
  }

  return {
    isAuthEnabled,
    isAuthenticated,
    isInitialized,
    init,
    login,
    logout,
  }
})
