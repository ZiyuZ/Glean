<script setup lang="ts">
import { useReaderConfig } from '@/composables/useReader'

const { fontSize, lineHeight, theme, brightness, padding, margin } = useReaderConfig()
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="true"
      data-settings-panel
      @click.stop
      class="reader-settings"
    >
      <div>
        <label class="block text-sm font-medium mb-2">
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
        <label class="block text-sm font-medium mb-2">
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
        <label class="block text-sm font-medium mb-2">主题</label>
        <select
          v-model="theme"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
        >
          <option value="light">明亮</option>
          <option value="sepia">护眼</option>
          <option value="dark">深色</option>
          <option value="night">夜间</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">
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
      <div>
        <label class="block text-sm font-medium mb-2">
          边距: {{ padding }}px
        </label>
        <input
          v-model.number="padding"
          type="range"
          min="32"
          max="128"
          step="8"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">
          段落间距: {{ margin }}px
        </label>
        <input
          v-model.number="margin"
          type="range"
          min="8"
          max="32"
          step="4"
          class="w-full"
        />
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
  padding: 1rem;
  max-height: 80vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dark .reader-settings {
  background-color: rgba(17, 24, 39, 0.95);
  border-top-color: rgb(31, 41, 55);
}
</style>

