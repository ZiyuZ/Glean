<script setup lang="ts">
import { DialogTitle } from '@headlessui/vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import BaseModal from './BaseModal.vue'

interface Props {
  show: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  type?: 'danger' | 'info'
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  confirmLabel: '确定',
  cancelLabel: '取消',
  type: 'danger',
  loading: false,
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'close'): void
}>()
</script>

<template>
  <BaseModal :show="show" :show-header="false" max-width="lg" @close="emit('close')">
    <div class="sm:flex sm:items-start">
      <!-- Icon -->
      <div
        class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full sm:mx-0 sm:h-10 sm:w-10"
        :class="type === 'danger' ? 'bg-red-100 dark:bg-red-900/20' : 'bg-blue-100 dark:bg-blue-900/20'"
      >
        <ExclamationTriangleIcon
          class="h-6 w-6"
          :class="type === 'danger' ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'"
        />
      </div>

      <!-- Content -->
      <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
        <DialogTitle as="h3" class="text-lg font-bold leading-6 text-gray-900 dark:text-white">
          {{ title }}
        </DialogTitle>
        <div class="mt-2 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
          {{ message }}
          <slot name="extra" />
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 sm:flex sm:flex-row-reverse gap-3">
      <button
        type="button"
        class="inline-flex w-full justify-center rounded-xl px-4 py-2.5 text-sm font-semibold text-white shadow-sm sm:w-auto transition-all active:scale-95 disabled:opacity-50"
        :class="type === 'danger' ? 'bg-red-600 hover:bg-red-500' : 'bg-blue-600 hover:bg-blue-500'"
        :disabled="loading"
        @click="emit('confirm')"
      >
        <span v-if="loading">处理中...</span>
        <span v-else>{{ confirmLabel }}</span>
      </button>
      <button
        type="button"
        class="mt-3 inline-flex w-full justify-center rounded-xl bg-white dark:bg-gray-700 px-4 py-2.5 text-sm font-semibold text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 sm:mt-0 sm:w-auto transition-all"
        @click="emit('close')"
      >
        {{ cancelLabel }}
      </button>
    </div>
  </BaseModal>
</template>
