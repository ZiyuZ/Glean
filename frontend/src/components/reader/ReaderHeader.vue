<script setup lang="ts">
import { ArrowLeftIcon, ListBulletIcon } from '@heroicons/vue/24/outline'
import { useHead } from '@unhead/vue'

defineProps<{
  title: string
  showTOC?: boolean
}>()

const emit = defineEmits<{
  back: []
  toggleTOC: []
}>()

useHead({
  meta: [
    {
      name: 'theme-color',
      content: '#fff',
    },
  ],
})
</script>

<template>
  <header class="reader-header">
    <div class="flex items-center justify-between">
      <button
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
        @click.stop="emit('back')"
      >
        <ArrowLeftIcon class="w-[20px] h-[20px]" />
        <span>返回</span>
      </button>
      <h1 class="text-lg font-semibold truncate flex-1 mx-4">
        {{ title || '加载中...' }}
      </h1>
      <button
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        @click.stop="emit('toggleTOC')"
      >
        <ListBulletIcon class="w-[20px] h-[20px]" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgb(229, 231, 235);
  padding: 0.75rem 1rem;
}

.dark .reader-header {
  background-color: rgba(17, 24, 39, 0.95);
  border-bottom-color: rgb(31, 41, 55);
}
</style>
