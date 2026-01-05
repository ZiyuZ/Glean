<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
}>()
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
          <slot name="actions" />
        </div>
      </div>

      <!-- Bottom: Extended content (Search, Filters) -->
      <div v-if="$slots.bottom" class="mt-3">
        <slot name="bottom" />
      </div>
    </div>
  </header>
</template>
