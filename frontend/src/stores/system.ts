import { defineStore } from 'pinia'
import { ref } from 'vue'
import { checkSystemHealth } from '@/api/system'

export const useSystemStore = defineStore('system', () => {
  const isServerReachable = ref(true)
  const isHealthChecking = ref(false)
  const unavailableReason = ref('无法连接服务器')
  const lastUnavailableAt = ref<number | null>(null)

  function markServerReachable() {
    isServerReachable.value = true
    unavailableReason.value = ''
    lastUnavailableAt.value = null
  }

  function markServerUnreachable(reason = '服务器暂时不可用') {
    if (isServerReachable.value) {
      lastUnavailableAt.value = Date.now()
    }
    isServerReachable.value = false
    unavailableReason.value = reason
  }

  async function probeServer() {
    if (isHealthChecking.value) {
      return isServerReachable.value
    }

    isHealthChecking.value = true
    try {
      await checkSystemHealth()
      markServerReachable()
      return true
    }
    catch {
      markServerUnreachable('无法连接到服务器，请稍后重试')
      return false
    }
    finally {
      isHealthChecking.value = false
    }
  }

  return {
    isServerReachable,
    isHealthChecking,
    unavailableReason,
    lastUnavailableAt,
    markServerReachable,
    markServerUnreachable,
    probeServer,
  }
})
