<script setup lang="ts">
import { useRegisterSW } from 'virtual:pwa-register/vue'
import { computed, ref } from 'vue'

// periodic sync is disabled, change the value to enable it, the period is in milliseconds
// You can remove onRegisteredSW callback and registerPeriodicSync function
const period = 0

const swActivated = ref(false)

/**
 * This function will register a periodic sync check every hour, you can modify the interval as needed.
 */
function registerPeriodicSync(swUrl: string, r: ServiceWorkerRegistration) {
  if (period <= 0)
    return

  setInterval(async () => {
    if ('onLine' in navigator && !navigator.onLine)
      return

    const resp = await fetch(swUrl, {
      cache: 'no-store',
      headers: {
        'cache': 'no-store',
        'cache-control': 'no-cache',
      },
    })

    if (resp?.status === 200)
      await r.update()
  }, period)
}

const { needRefresh, updateServiceWorker } = useRegisterSW({
  immediate: true,
  onRegisteredSW(swUrl, r) {
    if (period <= 0)
      return
    if (r?.active?.state === 'activated') {
      swActivated.value = true
      registerPeriodicSync(swUrl, r)
    }
    else if (r?.installing) {
      r.installing.addEventListener('statechange', (e) => {
        const sw = e.target as ServiceWorker
        swActivated.value = sw.state === 'activated'
        if (swActivated.value)
          registerPeriodicSync(swUrl, r)
      })
    }
  },
})

const title = computed(() => {
  if (needRefresh.value)
    return 'New content available, click on reload button to update.'
  return ''
})

function close() {
  needRefresh.value = false
}
</script>

<template>
  <div
    v-if="needRefresh"
    class="fixed right-0 bottom-0 m-4 p-3 border border-gray-300/30 rounded z-10 text-left shadow-md grid bg-white"
    aria-labelledby="toast-message" role="alert"
  >
    <div class="mb-2">
      <span id="toast-message">
        {{ title }}
      </span>
    </div>
    <div class="flex">
      <button
        type="button" class="block border border-gray-300/30 outline-none mr-1.5 rounded-sm py-0.5 px-2.5"
        @click="updateServiceWorker()"
      >
        Reload
      </button>
      <button
        type="button" class="border border-gray-300/30 outline-none mr-1.5 rounded-sm py-0.5 px-2.5"
        @click="close"
      >
        Close
      </button>
    </div>
  </div>
</template>
