<script setup lang="ts">
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { onUnmounted, ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import * as api from '@/api'
import BaseModal from '../ui/BaseModal.vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'scanFinished'): void
}>()

const scanStatus = ref<any>(null)
const scanning = ref(false)
const clearing = ref(false)
const isClearModalOpen = ref(false)
const systemVersion = ref<{ app_version: string, database_version: string } | null>(null)
const swInfo = ref<{
  supported: boolean
  controlled: boolean
  activeState: string
  waitingState: string
  installingState: string
  scriptUrl: string
  fingerprint: string
}>({
  supported: typeof window !== 'undefined' && 'serviceWorker' in navigator,
  controlled: false,
  activeState: 'unknown',
  waitingState: 'none',
  installingState: 'none',
  scriptUrl: '',
  fingerprint: '',
})
const swUpdating = ref(false)
const showVersionInfo = ref(false)
const showSwInfo = ref(false)
const buildVersion = import.meta.env.VITE_BUILD_VERSION || 'dev'
const buildTime = import.meta.env.VITE_BUILD_TIME || ''
const buildTimeDisplay = buildTime
  ? new Date(buildTime).toLocaleString('zh-CN', { hour12: false })
  : '-'

async function fetchVersion() {
  try {
    systemVersion.value = await api.getSystemVersion()
  }
  catch (err) {
    console.error('Failed to fetch system version:', err)
  }
}

async function sha256Hex(input: string): Promise<string> {
  const bytes = new TextEncoder().encode(input)
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return Array.from(new Uint8Array(digest))
    .map(v => v.toString(16).padStart(2, '0'))
    .join('')
}

async function refreshSwInfo() {
  if (!('serviceWorker' in navigator)) {
    return
  }
  try {
    const registration = await navigator.serviceWorker.getRegistration()
    swInfo.value.controlled = Boolean(navigator.serviceWorker.controller)
    swInfo.value.activeState = registration?.active?.state ?? 'none'
    swInfo.value.waitingState = registration?.waiting?.state ?? 'none'
    swInfo.value.installingState = registration?.installing?.state ?? 'none'
    swInfo.value.scriptUrl = registration?.active?.scriptURL ?? registration?.waiting?.scriptURL ?? ''
    swInfo.value.fingerprint = ''

    // 通过 no-store 拉取 sw.js 并显示指纹，便于确认是否切到了新 SW 版本
    const response = await fetch(`/sw.js?t=${Date.now()}`, { cache: 'no-store' })
    if (response.ok) {
      const content = await response.text()
      const hash = await sha256Hex(content)
      swInfo.value.fingerprint = hash.slice(0, 12)
    }
  }
  catch (err) {
    console.error('Failed to refresh service worker info:', err)
  }
}

async function forceUpdateServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    toast.error('当前环境不支持 Service Worker')
    return
  }
  swUpdating.value = true
  try {
    const registration = await navigator.serviceWorker.getRegistration()
    if (!registration) {
      toast.info('尚未注册 Service Worker，请先刷新页面')
      return
    }

    await registration.update()
    if (registration.waiting) {
      registration.waiting.postMessage({ type: 'SKIP_WAITING' })
    }

    await refreshSwInfo()

    if (registration.waiting) {
      toast.success('发现新版本，正在切换并刷新')
      const onControllerChange = () => {
        navigator.serviceWorker.removeEventListener('controllerchange', onControllerChange)
        window.location.reload()
      }
      navigator.serviceWorker.addEventListener('controllerchange', onControllerChange)
      // 兜底：某些环境可能没有触发 controllerchange
      window.setTimeout(() => window.location.reload(), 1500)
      return
    }

    toast.success('已检查更新，当前已是最新 SW')
  }
  catch (err) {
    console.error('Failed to force update service worker:', err)
    toast.error('SW 更新失败')
  }
  finally {
    swUpdating.value = false
  }
}

async function triggerScan(fullScan: boolean = false) {
  scanning.value = true
  try {
    await api.triggerScan(fullScan)
    await waitScanUntilFinished()
    emit('scanFinished')
  }
  catch (err) {
    console.error('Failed to trigger scan:', err)
    toast.error('启动扫描失败')
  }
  finally {
    scanning.value = false
  }
}

async function checkScanStatus() {
  try {
    scanStatus.value = await api.getScanStatus()
    if (scanning.value && !scanStatus.value.is_running) {
      toast.success('扫描任务已完成')
      return true
    }
    return false
  }
  catch (err) {
    console.error('Failed to get scan status:', err)
  }
}

async function waitScanUntilFinished() {
  while (scanning.value) {
    if (await checkScanStatus()) {
      break
    }
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
}

async function stopScan() {
  try {
    await api.stopScan()
    await checkScanStatus()
    emit('scanFinished')
  }
  catch (err) {
    console.error('Failed to stop scan:', err)
    toast.error('停止扫描失败')
  }
}

async function waitClearUntilFinished() {
  while (clearing.value) {
    try {
      scanStatus.value = await api.getScanStatus()
    }
    catch (err) {
      console.error('Failed to poll clear status:', err)
      await new Promise(resolve => setTimeout(resolve, 500))
      continue
    }
    if (!scanStatus.value?.is_clearing) {
      if (scanStatus.value?.clear_error) {
        toast.error(`清空失败：${scanStatus.value.clear_error}`)
      }
      else {
        toast.success('数据库已清空')
        emit('scanFinished')
      }
      clearing.value = false
      break
    }
    await new Promise(resolve => setTimeout(resolve, 500))
  }
}

async function clearDatabase() {
  isClearModalOpen.value = false
  try {
    await api.clearDatabase()
    clearing.value = true
    toast.info('正在清空数据库，请稍候…')
    await waitClearUntilFinished()
  }
  catch (err) {
    console.error('Failed to clear database:', err)
    toast.error('清空数据库失败')
  }
  finally {
    clearing.value = false
  }
}

let interval: number | null = null

function startPolling() {
  if (interval)
    return
  checkScanStatus()
  interval = setInterval(checkScanStatus, 1000)
}

function stopPolling() {
  if (interval) {
    clearInterval(interval)
    interval = null
  }
}

// Watch isOpen to start/stop polling
watch(() => props.isOpen, (val) => {
  if (val) {
    startPolling()
    fetchVersion()
    refreshSwInfo()
  }
  else {
    stopPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <BaseModal :show="isOpen" title="书库维护" @close="emit('close')">
    <div class="space-y-4">
      <!-- Scan Controls -->
      <div class="space-y-3">
        <button :disabled="scanning || clearing || scanStatus?.is_running || scanStatus?.is_clearing"
          class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          @click="triggerScan(false)">
          {{ scanStatus?.is_running ? '扫描中...' : '增量扫描' }}
        </button>

        <button v-if="!scanStatus?.is_running" :disabled="scanning || clearing || scanStatus?.is_clearing"
          class="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-xl font-medium transition-colors"
          @click="triggerScan(true)">
          全量扫描
        </button>

        <button v-if="scanStatus?.is_running"
          class="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors"
          @click="stopScan">
          停止扫描
        </button>

        <!-- Status -->
        <div v-if="scanStatus"
          class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <div v-if="scanStatus.is_clearing"
            class="text-amber-600 dark:text-amber-400 font-medium pb-2 border-b border-amber-200/60 dark:border-amber-900/40">
            正在清空数据库…
          </div>
          <div class="flex justify-between">
            <span>已扫描:</span>
            <span class="font-medium text-gray-900 dark:text-gray-200">{{ scanStatus.files_scanned }}</span>
          </div>
          <div class="flex justify-between">
            <span>新增书籍:</span>
            <span class="text-green-600 dark:text-green-400 font-medium">+{{ scanStatus.files_added }}</span>
          </div>
          <div class="flex justify-between">
            <span>更新书籍:</span>
            <span class="text-blue-600 dark:text-blue-400 font-medium">{{ scanStatus.files_updated }}</span>
          </div>
          <div class="pt-2 border-t border-gray-200 dark:border-gray-700 mt-2">
            <p class="text-xs text-gray-500 opacity-75 whitespace-nowrap overflow-hidden text-ellipsis w-64"
              style="direction: rtl; text-align: left;" :title="scanStatus.current_file">
              &lrm;{{ scanStatus.current_file || '等待启动扫描' }}
            </p>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <button :disabled="scanning || clearing || scanStatus?.is_running || scanStatus?.is_clearing"
            class="w-full py-3 px-4 bg-red-50 hover:bg-red-100 dark:bg-red-900/10 dark:hover:bg-red-900/20 disabled:opacity-50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 rounded-xl font-medium transition-colors"
            @click="isClearModalOpen = true">
            {{ scanStatus?.is_clearing ? '清空中…' : '清空数据库' }}
          </button>
          <p class="text-xs text-gray-500 mt-2 text-center">
            这将删除所有书籍和更读进度，但不会删除物理文件。
          </p>
        </div>

        <!-- Version Info -->
        <div class="space-y-2">
          <div
            class="rounded-lg border border-gray-200 dark:border-gray-700 text-[11px] text-gray-600 dark:text-gray-300">
            <button
              class="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              @click="showVersionInfo = !showVersionInfo">
              <span class="font-medium">版本信息</span>
              <span class="text-xs text-gray-400">{{ showVersionInfo ? '▾' : '▸' }}</span>
            </button>
            <div v-if="showVersionInfo" class="px-3 pb-2 space-y-0.5">
              <p>前端版本: {{ buildVersion }}</p>
              <p>构建时间: {{ buildTimeDisplay }}</p>
              <p>后端版本: {{ systemVersion?.app_version || '-' }}</p>
              <p>数据库 Schema: {{ systemVersion?.database_version || '-' }}</p>
            </div>
          </div>

          <div
            class="rounded-lg border border-gray-200 dark:border-gray-700 text-[11px] text-gray-600 dark:text-gray-300">
            <div
              class="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              @click="showSwInfo = !showSwInfo">
              <span class="font-medium">Service Worker</span>
              <span class="flex-1" />
              <button v-show="showSwInfo"
                class="mr-4 px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-[10px] disabled:opacity-60"
                :disabled="swUpdating || !swInfo.supported" @click="forceUpdateServiceWorker">
                {{ swUpdating ? '更新中...' : '强制检查并更新' }}
              </button>
              <span class="text-xs text-gray-400">{{ showSwInfo ? '▾' : '▸' }}</span>
            </div>
            <div v-if="showSwInfo" class="px-3 pb-2 space-y-1">
              <div class="space-y-0.5">
                <p>状态: {{ swInfo.supported ? '支持' : '不支持' }}</p>
                <p>控制页面: {{ swInfo.controlled ? '是' : '否' }}</p>
                <p>active: {{ swInfo.activeState }}, waiting: {{ swInfo.waitingState }}</p>
                <p v-if="swInfo.fingerprint">
                  指纹: {{ swInfo.fingerprint }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Clear Confirmation Modal -->
    <BaseModal :show="isClearModalOpen" title="确定清空数据库?" :show-close="false" max-width="lg"
      @close="isClearModalOpen = false">
      <div class="sm:flex sm:items-start">
        <div
          class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
          <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
        </div>
        <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
          <div class="mt-2">
            <p class="text-sm text-gray-500 dark:text-gray-400">
              所有阅读进度、章节数据和书架记录将被删除。此操作
              <span class="font-bold text-red-500">无法撤销</span>
              。(您的物理文件还是安全的)
            </p>
          </div>
        </div>
      </div>
      <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse gap-3">
        <button type="button"
          class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:w-auto"
          @click="clearDatabase">
          确定清空
        </button>
        <button type="button"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white dark:bg-gray-700 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 sm:mt-0 sm:w-auto"
          @click="isClearModalOpen = false">
          取消
        </button>
      </div>
    </BaseModal>
  </BaseModal>
</template>
