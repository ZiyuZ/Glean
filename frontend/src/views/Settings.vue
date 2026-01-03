<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useReaderConfig } from '@/composables/useReader'
import * as api from '@/api'

const { fontSize, lineHeight, theme, brightness } = useReaderConfig()
const scanStatus = ref<any>(null)
const scanning = ref(false)

async function triggerScan(fullScan: boolean = false) {
  scanning.value = true
  try {
    await api.triggerScan(fullScan)
    await checkScanStatus()
  } catch (err) {
    console.error('Failed to trigger scan:', err)
  } finally {
    scanning.value = false
  }
}

async function checkScanStatus() {
  try {
    scanStatus.value = await api.getScanStatus()
  } catch (err) {
    console.error('Failed to get scan status:', err)
  }
}

async function stopScan() {
  try {
    await api.stopScan()
    await checkScanStatus()
  } catch (err) {
    console.error('Failed to stop scan:', err)
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
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/95 dark:border-gray-800">
      <div class="px-4 py-3">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">设置</h1>
      </div>
    </header>

    <!-- Settings Content -->
    <main class="px-4 py-4 space-y-6">
      <!-- Reading Settings -->
      <section class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          阅读设置
        </h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              字体大小: {{ fontSize }}px
            </label>
            <input
              v-model.number="fontSize"
              type="range"
              min="12"
              max="32"
              step="1"
              class="w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              行高: {{ lineHeight.toFixed(1) }}
            </label>
            <input
              v-model.number="lineHeight"
              type="range"
              min="1.2"
              max="2.5"
              step="0.1"
              class="w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              主题
            </label>
            <select
              v-model="theme"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="light">明亮</option>
              <option value="sepia">护眼</option>
              <option value="dark">深色</option>
              <option value="night">夜间</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              亮度: {{ brightness }}%
            </label>
            <input
              v-model.number="brightness"
              type="range"
              min="0"
              max="100"
              step="1"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- Scan Settings -->
      <section class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          文件扫描
        </h2>

        <div class="space-y-3">
          <button
            @click="triggerScan(false)"
            :disabled="scanning || scanStatus?.is_running"
            class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors"
          >
            {{ scanning ? '扫描中...' : '增量扫描' }}
          </button>

          <button
            @click="triggerScan(true)"
            :disabled="scanning || scanStatus?.is_running"
            class="w-full py-3 px-4 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors"
          >
            全量扫描
          </button>

          <button
            v-if="scanStatus?.is_running"
            @click="stopScan"
            class="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors"
          >
            停止扫描
          </button>

          <div v-if="scanStatus" class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <p>已扫描: {{ scanStatus.files_scanned }}</p>
            <p>已添加: {{ scanStatus.files_added }}</p>
            <p>已更新: {{ scanStatus.files_updated }}</p>
            <p v-if="scanStatus.current_file">
              当前: {{ scanStatus.current_file }}
            </p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

