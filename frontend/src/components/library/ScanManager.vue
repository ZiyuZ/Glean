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
const isClearModalOpen = ref(false)

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

async function clearDatabase() {
  isClearModalOpen.value = false
  try {
    await api.clearDatabase()
    await checkScanStatus()
    emit('scanFinished')
  }
  catch (err) {
    console.error('Failed to clear database:', err)
    toast.error('清空数据库失败')
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
  <BaseModal
    :show="isOpen"
    title="书库维护"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <!-- Scan Controls -->
      <div class="space-y-3">
        <button
          :disabled="scanning || scanStatus?.is_running"
          class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          @click="triggerScan(false)"
        >
          {{ scanStatus?.is_running ? '扫描中...' : '增量扫描 (推荐)' }}
        </button>

        <button
          v-if="!scanStatus?.is_running"
          :disabled="scanning"
          class="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-xl font-medium transition-colors"
          @click="triggerScan(true)"
        >
          全量扫描
        </button>

        <button
          v-if="scanStatus?.is_running"
          class="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors"
          @click="stopScan"
        >
          停止扫描
        </button>

        <!-- Status -->
        <div v-if="scanStatus" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 text-sm text-gray-600 dark:text-gray-400 space-y-1">
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
          <div v-if="scanStatus.current_file" class="pt-2 border-t border-gray-200 dark:border-gray-700 mt-2">
            <p
              class="text-xs text-gray-500 opacity-75 whitespace-nowrap overflow-hidden text-ellipsis w-64"
              style="direction: rtl; text-align: left;"
              :title="scanStatus.current_file"
            >
              &lrm;{{ scanStatus.current_file }}
            </p>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            :disabled="scanning || scanStatus?.is_running"
            class="w-full py-3 px-4 bg-red-50 hover:bg-red-100 dark:bg-red-900/10 dark:hover:bg-red-900/20 disabled:opacity-50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 rounded-xl font-medium transition-colors"
            @click="isClearModalOpen = true"
          >
            清空数据库
          </button>
          <p class="text-xs text-gray-500 mt-2 text-center">
            这将删除所有书籍和更读进度，但不会删除物理文件。
          </p>
        </div>
      </div>
    </div>

    <!-- Clear Confirmation Modal -->
    <BaseModal
      :show="isClearModalOpen"
      title="确定清空数据库?"
      :show-close="false"
      max-width="lg"
      @close="isClearModalOpen = false"
    >
      <div class="sm:flex sm:items-start">
        <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
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
        <button
          type="button"
          class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:w-auto"
          @click="clearDatabase"
        >
          确定清空
        </button>
        <button
          type="button"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white dark:bg-gray-700 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 sm:mt-0 sm:w-auto"
          @click="isClearModalOpen = false"
        >
          取消
        </button>
      </div>
    </BaseModal>
  </BaseModal>
</template>
