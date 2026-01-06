<script setup lang="ts">
defineProps<{
  type: 'card' | 'list-item' | 'text'
  count?: number
}>()
</script>

<template>
  <div class="animate-pulse space-y-4">
    <!-- Card Style (for Discovery) -->
    <div v-if="type === 'card'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-for="i in (count || 4)" :key="i" class="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 h-32 flex flex-col justify-between">
        <div class="space-y-3">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
        </div>
        <div class="flex gap-2">
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16" />
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20" />
        </div>
      </div>
    </div>

    <!-- List Item Style (for Bookshelf) -->
    <div v-if="type === 'list-item'" class="space-y-3">
      <div v-for="i in (count || 6)" :key="i" class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 flex items-center justify-between border border-gray-100 dark:border-gray-800">
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
        </div>
        <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>
    </div>
  </div>
</template>
