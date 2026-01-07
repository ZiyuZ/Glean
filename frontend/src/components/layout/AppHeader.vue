<script setup lang="ts">
import type { Component } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'

defineProps<{
  title?: string
  subtitle?: string
  actionIcon?: Component
  actionLoading?: boolean
  actionTitle?: string
  // Search props
  searchModelValue?: string
  searchPlaceholder?: string
  showSearch?: boolean
}>()

const emit = defineEmits<{
  (e: 'action'): void
  (e: 'update:searchModelValue', value: string): void
  (e: 'searchInput'): void
}>()

function onInput(e: Event) {
  const value = (e.target as HTMLInputElement).value
  emit('update:searchModelValue', value)
  emit('searchInput')
}

function clearSearch() {
  emit('update:searchModelValue', '')
  emit('searchInput')
}
</script>

<template>
  <header
    class="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/95 dark:border-gray-800 transition-colors duration-300 pt-[env(safe-area-inset-top)]"
  >
    <div class="px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Left: Title & Subtitle -->
        <div>
          <slot name="title">
            <h1 v-if="title" class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ title }}
            </h1>
          </slot>
          <slot name="subtitle">
            <p v-if="subtitle" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {{ subtitle }}
            </p>
          </slot>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center gap-2">
          <slot name="actions">
            <button
              v-if="actionIcon"
              :disabled="actionLoading"
              :title="actionTitle"
              class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 active:bg-gray-200 dark:active:bg-gray-700 active:scale-95 text-gray-600 dark:text-gray-400 disabled:opacity-50 transition-all"
              @click="$emit('action')"
            >
              <component
                :is="actionIcon"
                class="w-6 h-6"
                :class="{ 'animate-spin': actionLoading }"
              />
            </button>
          </slot>
        </div>
      </div>

      <!-- Search Bar Integrated -->
      <div v-if="showSearch" class="mt-3 relative">
        <input
          :value="searchModelValue"
          type="text"
          :placeholder="searchPlaceholder || '搜索...'"
          class="w-full pl-10 pr-10 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
          @input="onInput"
        >
        <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <MagnifyingGlassIcon class="w-5 h-5" />
        </div>
        <button
          v-if="searchModelValue"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          @click="clearSearch"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Bottom: Extended content (Filters, etc) -->
      <div v-if="$slots.bottom" class="mt-3">
        <slot name="bottom" />
      </div>
    </div>
  </header>
</template>
