<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Toaster } from 'vue-sonner'
import BottomNav from '@/components/layout/BottomNav.vue'
import ServiceUnavailableOverlay from '@/components/layout/ServiceUnavailableOverlay.vue'
import { useAuthStore } from '@/stores/auth'
import { useSystemStore } from '@/stores/system'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const systemStore = useSystemStore()

const showNav = computed(() => !route.meta.hideNav && systemStore.isServerReachable)

let healthProbeTimer: number | null = null
let lastProbeAt = 0
const HEALTHY_PROBE_INTERVAL = 30000
const UNHEALTHY_PROBE_INTERVAL = 1500

function handleUnauthorized() {
  authStore.logout()
  router.push('/login')
}

function handleServerUnreachable(event: Event) {
  const detail = (event as CustomEvent<{ reason?: string }>).detail
  systemStore.markServerUnreachable(detail?.reason || '服务器暂时不可用')
}

function retryConnection() {
  void systemStore.probeServer()
}

function triggerImmediateProbe() {
  if (!navigator.onLine) {
    handleOffline()
    return
  }
  const now = Date.now()
  // 避免多个并发失败请求导致重复探活
  if (now - lastProbeAt < 1000) {
    return
  }
  lastProbeAt = now
  void systemStore.probeServer()
}

function handleOffline() {
  systemStore.markServerUnreachable('网络已断开，无法连接服务器')
}

function handleOnline() {
  triggerImmediateProbe()
}

function scheduleNextProbe() {
  const nextInterval = systemStore.isServerReachable
    ? HEALTHY_PROBE_INTERVAL
    : UNHEALTHY_PROBE_INTERVAL

  healthProbeTimer = window.setTimeout(async () => {
    if (!navigator.onLine) {
      handleOffline()
      scheduleNextProbe()
      return
    }

    await systemStore.probeServer()
    scheduleNextProbe()
  }, nextInterval)
}

function startHealthProbe() {
  if (healthProbeTimer !== null) {
    window.clearTimeout(healthProbeTimer)
  }
  scheduleNextProbe()
}

function stopHealthProbe() {
  if (healthProbeTimer !== null) {
    window.clearTimeout(healthProbeTimer)
    healthProbeTimer = null
  }
}

onMounted(() => {
  window.addEventListener('auth:unauthorized', handleUnauthorized)
  window.addEventListener('server:unreachable', handleServerUnreachable)
  window.addEventListener('server:probe-health', triggerImmediateProbe)
  window.addEventListener('offline', handleOffline)
  window.addEventListener('online', handleOnline)
  if (!navigator.onLine) {
    handleOffline()
  }
  else {
    triggerImmediateProbe()
  }
  startHealthProbe()
})

onUnmounted(() => {
  window.removeEventListener('auth:unauthorized', handleUnauthorized)
  window.removeEventListener('server:unreachable', handleServerUnreachable)
  window.removeEventListener('server:probe-health', triggerImmediateProbe)
  window.removeEventListener('offline', handleOffline)
  window.removeEventListener('online', handleOnline)
  stopHealthProbe()
})
</script>

<template>
  <Toaster position="top-center" />
  <div
    class="fixed inset-0 w-full flex flex-col overflow-hidden bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100"
  >
    <div class="flex-1 min-h-0 w-full relative">
      <router-view />
    </div>
    <BottomNav v-if="showNav" class="flex-shrink-0" />
    <ServiceUnavailableOverlay
      v-if="!systemStore.isServerReachable"
      :checking="systemStore.isHealthChecking"
      :reason="systemStore.unavailableReason"
      @retry="retryConnection"
    />
  </div>
</template>

<style>
/* 全局样式 */
* {
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 暗色模式滚动条 */
.dark ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
