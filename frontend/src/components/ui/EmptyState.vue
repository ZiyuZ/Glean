<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  description?: string
  icon?: Component
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div v-if="icon" class="mb-4 p-4 rounded-full bg-gray-50 dark:bg-gray-800/50 text-gray-400 dark:text-gray-500 ring-1 ring-gray-100 dark:ring-gray-800">
      <component :is="icon" class="w-10 h-10" />
    </div>
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      {{ title }}
    </h3>
    <p v-if="description" class="mt-1 text-sm text-gray-500 dark:text-gray-400 max-w-xs mx-auto">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="mt-6">
      <slot name="actions" />
    </div>
  </div>
</template>
