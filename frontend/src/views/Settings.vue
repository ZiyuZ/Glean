<script setup lang="ts">
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { onMounted, onUnmounted, ref } from 'vue'
import { toast } from 'vue-sonner'
import * as api from '@/api'

const scanStatus = ref<any>(null)
const scanning = ref(false)
const isClearModalOpen = ref(false)

async function triggerScan(fullScan: boolean = false) {
  scanning.value = true
  try {
    await api.triggerScan(fullScan)
    toast.info('扫描任务已启动')
    await waitScanUntilFinished()
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
    toast.info('已请求停止扫描')
    await checkScanStatus()
  }
  catch (err) {
    console.error('Failed to stop scan:', err)
    toast.error('停止扫描失败')
  }
}

function confirmClearDatabase() {
  isClearModalOpen.value = true
}

async function clearDatabase() {
  isClearModalOpen.value = false
  try {
    await api.clearDatabase()
    toast.success('数据库已清空')
    await checkScanStatus()
  }
  catch (err) {
    console.error('Failed to clear database:', err)
    toast.error('清空数据库失败')
  }
}

onMounted(() => {
  checkScanStatus()
  // 定期检查扫描状态
  const interval = setInterval(checkScanStatus, 1000)
  onUnmounted(() => clearInterval(interval))
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <header
      class="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/95 dark:border-gray-800"
    >
      <div class="px-4 py-3">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          设置
        </h1>
      </div>
    </header>

    <!-- Settings Content -->
    <main class="px-4 py-4 space-y-6">
      <!-- Scan Settings -->
      <section class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          文件扫描
        </h2>

        <div class="space-y-3">
          <button
            :disabled="scanning || scanStatus?.is_running" class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors"
            @click="triggerScan(false)"
          >
            {{ scanStatus?.is_running ? '扫描中...' : '增量扫描' }}
          </button>

          <button
            :disabled="scanning || scanStatus?.is_running" class="w-full py-3 px-4 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors"
            @click="triggerScan(true)"
          >
            {{ scanStatus?.is_running ? '扫描中...' : '全量扫描' }}
          </button>

          <button
            v-if="scanStatus?.is_running" class="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors"
            @click="stopScan"
          >
            停止扫描
          </button>

          <div v-if="scanStatus" class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <p>已处理: {{ scanStatus.files_scanned }}</p>
            <p>已添加: {{ scanStatus.files_added }}</p>
            <p>已更新: {{ scanStatus.files_updated }}</p>
            <p>待处理: {{ scanStatus.total_files - scanStatus.files_scanned }}</p>
            <p v-if="scanStatus.current_file">
              当前: {{ scanStatus.current_file }}
            </p>
          </div>

          <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              :disabled="scanning || scanStatus?.is_running"
              class="w-full py-3 px-4 bg-red-50 hover:bg-red-100 disabled:bg-gray-100 text-red-600 border border-red-200 rounded-xl font-medium transition-colors"
              @click="confirmClearDatabase"
            >
              清空数据库
            </button>
            <p class="text-xs text-gray-500 mt-2 text-center">
              这将删除所有书籍和更读进度，但不会删除物理文件。
            </p>
          </div>
        </div>
      </section>
    </main>

    <!-- Clear Database Confirmation Modal -->
    <TransitionRoot as="template" :show="isClearModalOpen">
      <Dialog as="div" class="relative z-50" @close="isClearModalOpen = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
                      清空数据库?
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        确定要清空数据库吗？这将删除所有书籍记录、章节数据和您的阅读进度。此操作无法撤销。
                        (物理文件保留)
                      </p>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
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
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>
