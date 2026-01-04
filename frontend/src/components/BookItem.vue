<script setup lang="ts">
import type { Book } from '@/types/api'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { CheckCircleIcon, EllipsisHorizontalIcon, StarIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'

defineProps<{
  book: Book
}>()

const emit = defineEmits<{
  (e: 'open', book: Book): void
  (e: 'toggleStar', book: Book): void
  (e: 'delete', book: Book): void
}>()

function formatDate(timestamp: number | null): string {
  if (!timestamp)
    return '未读'
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1)
    return '刚刚'
  if (minutes < 60)
    return `${minutes}分钟前`
  if (hours < 24)
    return `${hours}小时前`
  if (days === 1)
    return '昨天'
  if (days < 30)
    return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <div
    class="relative bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
    @click="emit('open', book)"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
          {{ book.title }}
        </h2>
        <div class="flex items-center gap-2 mt-1 h-4">
          <span class="text-sm text-gray-500 dark:text-gray-400 leading-none">
            {{ formatDate(book.last_read_time) }}
          </span>
          <CheckCircleIcon v-if="book.is_finished" class="w-4 h-4 text-green-500" title="已读完" />
        </div>
      </div>
      <div class="flex items-center gap-2 ml-4">
        <button
          class="p-2 rounded-lg transition-colors" :class="[
            book.is_starred
              ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
              : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700',
          ]"
          @click.stop="emit('toggleStar', book)"
        >
          <component :is="book.is_starred ? StarIconSolid : StarIcon" class="w-5 h-5" />
        </button>
        <Menu as="div" class="relative inline-block text-left" @click.stop>
          <MenuButton
            class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            <EllipsisHorizontalIcon class="w-5 h-5" />
          </MenuButton>

          <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <MenuItems
              class="absolute right-0 mt-2 w-32 origin-top-right divide-y divide-gray-100 rounded-xl bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-20"
            >
              <div class="px-1 py-1">
                <MenuItem v-slot="{ active }">
                  <button
                    class="group flex w-full items-center rounded-lg px-2 py-2 text-sm"
                    :class="[
                      active ? 'bg-red-50 text-red-600 dark:bg-red-900/20' : 'text-gray-700 dark:text-gray-200',
                    ]"
                    @click="emit('delete', book)"
                  >
                    <TrashIcon class="mr-2 h-4 w-4" aria-hidden="true" />
                    删除
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </transition>
        </Menu>
      </div>
    </div>
  </div>
</template>
