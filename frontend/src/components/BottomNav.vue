<script setup lang="ts">
import { ArchiveBoxIcon, BookOpenIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', name: '书架', icon: BookOpenIcon },
  { path: '/discovery', name: '发现', icon: MagnifyingGlassIcon },
  { path: '/library', name: '书库', icon: ArchiveBoxIcon },
]

const currentPath = computed(() => route.path)

function navigate(path: string) {
  router.push(path)
}
</script>

<template>
  <nav
    class="w-full bg-white border-t border-gray-200 dark:bg-gray-900 dark:border-gray-800 pb-[env(safe-area-inset-bottom)]"
  >
    <div class="flex justify-around items-center h-16 px-4">
      <button
        v-for="item in navItems" :key="item.path" class="flex flex-col items-center justify-center flex-1 h-full transition-colors" :class="[
          currentPath === item.path
            ? 'text-blue-600 dark:text-blue-400'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200',
        ]" @click="navigate(item.path)"
      >
        <component :is="item.icon" class="w-[24px] h-[24px] mb-1" />
        <span class="text-xs font-medium">{{ item.name }}</span>
      </button>
    </div>
  </nav>
</template>
