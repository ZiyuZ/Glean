<script setup lang="ts">
interface Props {
  checking: boolean
  reason?: string
}

withDefaults(defineProps<Props>(), {
  reason: '服务器暂时不可用',
})

const emit = defineEmits<{
  retry: []
}>()

function handleRetry() {
  emit('retry')
}
</script>

<template>
  <div class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/70 backdrop-blur-sm p-6">
    <div class="w-full max-w-md rounded-2xl border border-white/20 bg-slate-900/95 p-6 text-slate-100 shadow-2xl">
      <div class="mb-4 flex items-center gap-3">
        <div class="h-3 w-3 rounded-full bg-amber-400" />
        <h2 class="text-xl font-semibold tracking-wide">
          服务不可用
        </h2>
      </div>

      <p class="text-sm leading-6 text-slate-300">
        {{ reason }}
      </p>

      <p class="mt-2 text-xs text-slate-400">
        当前操作已暂时锁定，避免误操作导致连续失败。
      </p>

      <button
        class="mt-6 inline-flex w-full items-center justify-center rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="checking"
        @click="handleRetry"
      >
        {{ checking ? '检测中...' : '重试连接' }}
      </button>
    </div>
  </div>
</template>
