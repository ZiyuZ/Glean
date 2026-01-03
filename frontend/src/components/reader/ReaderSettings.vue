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

const { fontSize, lineHeight, theme, brightness, paddingX, paddingY, margin, enableAnimation } = useReaderConfig()

function getThemeBg(t: string) {
  switch (t) {
    case 'light': return '#fbfbfb'
    case 'sepia': return '#f4ecd8'
    case 'dark': return '#1a1a1a'
    case 'night': return '#000000'
    default: return '#ffffff'
  }
}
// Configuration ranges for settings
const settingRanges = {
  fontSize: { min: 12, max: 36, step: 1 },
  lineHeight: { min: 1.2, max: 2.4, step: 0.1 },
  margin: { min: 0, max: 40, step: 1 },
  paddingX: { min: 0, max: 40, step: 1 },
  paddingY: { min: 0, max: 60, step: 1 },
  brightness: { min: 10, max: 100, step: 1 },
}
</script>

<template>
  <Transition name="slide-up">
    <div v-if="true" data-settings-panel class="reader-settings no-scrollbar" @click.stop>
      <div class="mb-5">
        <p class="text-lg font-bold text-gray-900 dark:text-gray-50">
          阅读设置
        </p>
      </div>

      <div class="divide-y divide-gray-100 dark:divide-gray-700/60">
        <!-- Font Size -->
        <div class="grid grid-cols-[100px,1fr] items-center gap-4 py-4">
          <div class="space-y-0.5">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              字号
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-400">A-</span>
            <input v-model.number="fontSize" type="range" :min="settingRanges.fontSize.min" :max="settingRanges.fontSize.max" :step="settingRanges.fontSize.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
            <span class="text-xs text-gray-400">A+</span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200 tabular-nums min-w-[2.5rem] text-right">
              {{ fontSize }}
            </span>
          </div>
        </div>

        <!-- Theme -->
        <div class="py-4">
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              背景主题
            </p>
          </div>
          <div class="grid grid-cols-4 gap-3">
            <button
              v-for="option in themeOptions" :key="option.value" type="button"
              class="flex flex-col items-center justify-center gap-1 py-2 rounded-xl border-2 transition-all duration-200"
              :class="[
                theme === option.value
                  ? 'border-blue-500 shadow-sm scale-[1.02]'
                  : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-800 scale-100',
                option.value === 'light' ? 'bg-[#fbfbfb] text-gray-800' : '',
                option.value === 'sepia' ? 'bg-[#f4ecd8] text-[#5b4636]' : '',
                option.value === 'dark' ? 'bg-[#1a1a1a] text-[#cecece]' : '',
                option.value === 'night' ? 'bg-[#000000] text-[#888888]' : '',
              ]"
              @click="theme = option.value"
            >
              <div class="w-6 h-6 rounded-full border border-black/10 dark:border-white/10" :style="{ background: getThemeBg(option.value) }" />
              <span class="text-xs font-medium">{{ option.label }}</span>
            </button>
          </div>
        </div>

        <!-- Line Height & Margin & Padding -->
        <div class="space-y-6 py-4">
          <!-- Row 1: Line Height & Margin -->
          <div class="grid grid-cols-2 gap-6">
            <div class="space-y-3">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
                行高
              </p>
              <div class="flex items-center gap-2">
                <input v-model.number="lineHeight" type="range" :min="settingRanges.lineHeight.min" :max="settingRanges.lineHeight.max" :step="settingRanges.lineHeight.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
                <span class="text-xs text-gray-500 w-6 text-right">{{ lineHeight }}</span>
              </div>
            </div>
            <div class="space-y-3">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
                段间距
              </p>
              <div class="flex items-center gap-2">
                <input v-model.number="margin" type="range" :min="settingRanges.margin.min" :max="settingRanges.margin.max" :step="settingRanges.margin.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
                <span class="text-xs text-gray-500 w-6 text-right">{{ margin }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 2: Padding X & Y -->
        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-3">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              水平边距
            </p>
            <div class="flex items-center gap-2">
              <input v-model.number="paddingX" type="range" :min="settingRanges.paddingX.min" :max="settingRanges.paddingX.max" :step="settingRanges.paddingX.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
              <span class="text-xs text-gray-500 w-6 text-right">{{ paddingX }}</span>
            </div>
          </div>
          <div class="space-y-3">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
              垂直边距
            </p>
            <div class="flex items-center gap-2">
              <input v-model.number="paddingY" type="range" :min="settingRanges.paddingY.min" :max="settingRanges.paddingY.max" :step="settingRanges.paddingY.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
              <span class="text-xs text-gray-500 w-6 text-right">{{ paddingY }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Animation Toggle (SelectButton style) -->
      <div class="grid grid-cols-[100px,1fr] items-center gap-4 py-4">
        <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
          翻页动画
        </p>
        <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all"
            :class="enableAnimation ? 'bg-white dark:bg-gray-700 shadow text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-900 dark:hover:text-gray-300'"
            @click="enableAnimation = true"
          >
            开启
          </button>
          <button
            class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all"
            :class="!enableAnimation ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-gray-100' : 'text-gray-500 hover:text-gray-900 dark:hover:text-gray-300'"
            @click="enableAnimation = false"
          >
            关闭
          </button>
        </div>
      </div>

      <!-- Brightness -->
      <div class="grid grid-cols-[60px,1fr] items-center gap-4 py-4">
        <p class="text-sm font-medium text-gray-900 dark:text-gray-50">
          亮度
        </p>
        <div class="flex items-center gap-3">
          <input v-model.number="brightness" type="range" :min="settingRanges.brightness.min" :max="settingRanges.brightness.max" :step="settingRanges.brightness.step" class="flex-1 accent-blue-500 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-200 tabular-nums min-w-[2.5rem] text-right">
            {{ brightness }}%
          </span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.reader-settings {
  /* Positioning handled by parent */
  width: 100%;
  max-height: 72vh;
  overflow-y: auto;
}
</style>
