<script setup lang="ts">
import type { ReaderConfig } from '@/composables/useReader'
import { useReaderConfig } from '@/composables/useReader'

interface ThemeOption { value: ReaderConfig['theme'], label: string }

const themeOptions: ThemeOption[] = [
  { value: 'light', label: '明亮' },
  { value: 'sepia', label: '护眼' },
  { value: 'dark', label: '深色' },
  { value: 'night', label: '夜间' },
]

const { fontSize, lineHeight, theme, brightness, padding, margin } = useReaderConfig()
</script>

<template>
  <Transition name="slide-up">
    <div v-if="true" data-settings-panel class="reader-settings" @click.stop>
      <div class="flex items-center justify-between mb-3">
        <div>
          <p class="text-sm font-semibold text-gray-900 dark:text-gray-50">
            阅读器样式
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            仅作用于阅读区域
          </p>
        </div>
        <span
          class="text-[11px] px-2 py-1 rounded-full bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-200 border border-blue-100 dark:border-blue-500/30"
        >
          Reader only
        </span>
      </div>

      <div class="divide-y divide-gray-100 dark:divide-gray-700/60">
        <div class="grid grid-cols-[120px,1fr] items-center gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              字体大小
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              12 - 32 px
            </p>
          </div>
          <div class="flex items-center gap-3">
            <input v-model.number="fontSize" type="range" min="12" max="32" step="1" class="flex-1 accent-blue-500">
            <span class="text-sm text-gray-700 dark:text-gray-200 tabular-nums min-w-12 text-right">
              {{ fontSize }}px
            </span>
          </div>
        </div>

        <div class="grid grid-cols-[120px,1fr] items-center gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              行高
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              舒适的行间距
            </p>
          </div>
          <div class="flex items-center gap-3">
            <input
              v-model.number="lineHeight" type="range" min="1.2" max="2.5" step="0.1"
              class="flex-1 accent-blue-500"
            >
            <span class="text-sm text-gray-700 dark:text-gray-200 tabular-nums min-w-12 text-right">
              {{ lineHeight.toFixed(1) }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-[120px,1fr] items-start gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              阅读主题
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              背景与文字配色
            </p>
          </div>
          <div class="flex flex-wrap gap-2" role="group" aria-label="阅读主题">
            <button
              v-for="option in themeOptions" :key="option.value" type="button" class="px-3 py-2 rounded-lg border text-sm font-medium transition shadow-sm"
              :class="[
                theme === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-500/15 dark:text-blue-100'
                  : 'border-gray-200 bg-gray-50 text-gray-700 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200',
              ]" @click="theme = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <div class="grid grid-cols-[120px,1fr] items-center gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              亮度
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              0 - 100%
            </p>
          </div>
          <div class="flex items-center gap-3">
            <input v-model.number="brightness" type="range" min="0" max="100" step="1" class="flex-1 accent-blue-500">
            <span class="text-sm text-gray-700 dark:text-gray-200 tabular-nums min-w-12 text-right">
              {{ brightness }}%
            </span>
          </div>
        </div>

        <div class="grid grid-cols-[120px,1fr] items-center gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              页边距
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              32 - 128 px
            </p>
          </div>
          <div class="flex items-center gap-3">
            <input v-model.number="padding" type="range" min="32" max="128" step="8" class="flex-1 accent-blue-500">
            <span class="text-sm text-gray-700 dark:text-gray-200 tabular-nums min-w-12 text-right">
              {{ padding }}px
            </span>
          </div>
        </div>

        <div class="grid grid-cols-[120px,1fr] items-center gap-4 py-3">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              段落间距
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              8 - 32 px
            </p>
          </div>
          <div class="flex items-center gap-3">
            <input v-model.number="margin" type="range" min="8" max="32" step="4" class="flex-1 accent-blue-500">
            <span class="text-sm text-gray-700 dark:text-gray-200 tabular-nums min-w-12 text-right">
              {{ margin }}px
            </span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.reader-settings {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.95);
  border-top: 1px solid rgb(229, 231, 235);
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.08);
  padding: 1.25rem 1.25rem 1.5rem;
  max-height: 72vh;
  overflow-y: auto;
}

.dark .reader-settings {
  background-color: rgba(17, 24, 39, 0.95);
  border-top-color: rgb(31, 41, 55);
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.3);
}
</style>
