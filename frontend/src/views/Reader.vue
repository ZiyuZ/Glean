<script setup lang="ts">
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ArrowLeftIcon, ChevronLeftIcon, ChevronRightIcon, Cog6ToothIcon, ListBulletIcon } from '@heroicons/vue/24/outline'
import { useHead } from '@unhead/vue'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ReaderSettings from '@/components/reader/ReaderSettings.vue'
import ReaderTOC from '@/components/reader/ReaderTOC.vue'
import { useReaderConfig } from '@/composables/useReader'
import { useReaderStore } from '@/stores/reader'

const route = useRoute()
const router = useRouter()
const readerStore = useReaderStore()
const { fontSize, lineHeight, theme, brightness, paddingX, paddingY, margin, enableAnimation } = useReaderConfig()

// --- State ---
// contentRef holds the text container
const contentRef = ref<HTMLElement | null>(null)
const currentPage = ref(0)
const totalPages = ref(1)
const isMenuOpen = ref(false)
const showTOC = ref(false)
const showSettings = ref(false)
const isDragging = ref(false)

// --- Theme & Styles ---
const themeColors = computed(() => {
  const themes = {
    light: { bg: '#fbfbfb', text: '#333333' },
    sepia: { bg: '#f4ecd8', text: '#5b4636' },
    dark: { bg: '#1a1a1a', text: '#cecece' },
    night: { bg: '#000000', text: '#888888' },
  }
  return themes[theme.value]
})

useHead({
  title: readerStore.currentBook?.title,
  meta: [
    {
      name: 'theme-color',
      content: themeColors.value.bg,
    },
  ],
})

const containerStyle = computed(() => ({
  backgroundColor: themeColors.value.bg,
  color: themeColors.value.text,
  filter: `brightness(${brightness.value}%)`,
}))

// Styles for the paging content
// Dynamic styles only
const contentTextStyle = computed(() => ({
  fontSize: `${fontSize.value}px`,
  lineHeight: lineHeight.value,
  // Fix for drift:
  // 1. Container width is 100vw
  // 2. We want content to have horizontal padding X
  // 3. Stride must be exactly 100vw to match translation
  // Solution:
  // - Column Gap = 2 * paddingX
  // - Padding Left = paddingX
  // - Padding Right = paddingX
  // Result: Visible Width = 100vw - 2*X.
  // Next column starts at: X (start) + (100vw - 2X) (width) + 2X (gap) = 100vw + X.
  // Relative to next page viewport (0), it starts at X.
  // This maintains perfect alignment.
  columnGap: `${paddingX.value * 2}px`,
  paddingTop: `${paddingY.value}px`,
  paddingBottom: `${paddingY.value}px`,
  paddingLeft: `${paddingX.value}px`,
  paddingRight: `${paddingX.value}px`,

  // Transformation for Paging
  transform: `translateX(-${currentPage.value * 100}vw)`,
  transition: (enableAnimation.value && !isDragging.value) ? 'transform 0.3s ease-out' : 'none',
}))

// --- Content Processing ---
const paragraphs = computed(() => {
  if (!readerStore.currentContent)
    return []
  return readerStore.currentContent
    .split('\n')
    .filter(line => line.trim().length > 0)
    .map(line => line.trim())
})

// --- Core Logic: Rendering ---
async function updateMetrics() {
  await nextTick()
  if (!contentRef.value)
    return

  // In column layout, scrollWidth is the total width of all columns
  const fullWidth = contentRef.value.scrollWidth
  const viewWidth = window.innerWidth

  // Calculate total pages
  // Math.ceil is safe. sometimes scrollWidth is 1-2px off due to subpixel rendering, typically handled by floor or slight tolerance, but ceil is standard for columns.
  totalPages.value = Math.max(1, Math.ceil(fullWidth / viewWidth))

  // Clamp current page
  if (currentPage.value >= totalPages.value) {
    currentPage.value = totalPages.value - 1
  }
}

// --- Navigation ---
function nextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
  }
  else if (readerStore.hasNextChapter) {
    loadChapter(readerStore.currentChapterIndex! + 1)
  }
}

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
  }
  else if (readerStore.hasPreviousChapter) {
    loadChapter(readerStore.currentChapterIndex! - 1, 'end')
  }
}

async function loadChapter(index: number, position: 'start' | 'end' = 'start') {
  if (!readerStore.currentBook)
    return

  await saveProgress()
  await readerStore.loadChapter(index)
  await updateMetrics()

  if (position === 'start') {
    currentPage.value = 0
  }
  else {
    currentPage.value = Math.max(0, totalPages.value - 1)
  }
}

async function init() {
  const bookId = Number(route.params.bookId)
  if (Number.isNaN(bookId)) {
    router.push('/')
    return
  }
  try {
    await readerStore.loadBook(bookId)
    await updateMetrics()

    // Restore page progress
    if (readerStore.currentBook?.chapter_offset && readerStore.currentContent) {
      const contentLength = readerStore.currentContent.length
      if (contentLength > 0) {
        // Calculate progress ratio from offset
        const progress = readerStore.currentBook.chapter_offset / contentLength
        // Map to page number
        const page = Math.round(progress * totalPages.value)
        currentPage.value = Math.min(Math.max(0, page), totalPages.value - 1)
      }
    }
  }
  catch (e) {
    console.error(e)
  }
}

async function saveProgress() {
  if (readerStore.currentBook && readerStore.currentChapterIndex !== null) {
    let offset = 0
    // Estimate char offset based on current page
    if (readerStore.currentContent && totalPages.value > 1) {
      const contentLength = readerStore.currentContent.length
      // Calculate start of page ratio
      const progress = currentPage.value / totalPages.value
      offset = Math.floor(progress * contentLength)
    }

    await readerStore.saveProgress(offset)
  }
}

// --- Interaction: 3x3 Grid ---
function handleGridClick(index: number) {
  // 1 2 3    ↑ ↑ ↓
  // 4 5 6 => ↓ ○ ↓
  // 7 8 9    ↓ ↓ ↓

  // Center: 5 -> Menu
  if (index === 5) {
    isMenuOpen.value = !isMenuOpen.value
    return
  }

  // Left: 1, 2 -> Prev
  if (index === 1 || index === 2) {
    prevPage()
    return
  }

  // Right (the rest): 3, 4, 6, 7, 8, 9 -> Next
  nextPage()
}

// --- Lifecycle ---
onMounted(() => {
  init()
  window.addEventListener('resize', updateMetrics)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateMetrics)
  saveProgress()
})

watch([fontSize, lineHeight, paddingX, paddingY, margin], updateMetrics)
</script>

<template>
  <div
    class="reader-app relative w-full h-screen overflow-hidden select-none transition-colors duration-300"
    :style="containerStyle"
  >
    <!-- 3x3 Interaction Grid Overlay -->
    <div
      v-if="!isMenuOpen && !showSettings && !showTOC"
      class="absolute inset-0 z-40 grid grid-cols-3 grid-rows-3"
    >
      <div
        v-for="i in 9"
        :key="i"
        class="cursor-pointer"
        @click.stop="handleGridClick(i)"
      />
    </div>

    <!-- Mask to close menu when clicking outside (if menu is open) -->
    <div
      v-else
      class="absolute inset-0 z-40"
      @click="isMenuOpen = false; showSettings = false; showTOC = false"
    />

    <!-- Header -->
    <transition name="fade">
      <div v-if="isMenuOpen" class="absolute top-0 left-0 w-full z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur shadow-sm pt-[env(safe-area-inset-top)] p-4 flex justify-between items-center" @click.stop>
        <div class="flex items-center gap-4 text-gray-700 dark:text-gray-200 mt-2">
          <button @click="router.back()">
            <ArrowLeftIcon class="w-6 h-6" />
          </button>
          <span class="font-medium truncate max-w-[200px]">{{ readerStore.currentBook?.title }}</span>
        </div>
        <div class="flex gap-4 mt-2">
          <button @click="showTOC = true; isMenuOpen = false">
            <ListBulletIcon class="w-6 h-6" />
          </button>
          <button @click="showSettings = true; isMenuOpen = false">
            <Cog6ToothIcon class="w-6 h-6" />
          </button>
        </div>
      </div>
    </transition>

    <!-- Footer -->
    <transition name="fade">
      <div v-if="isMenuOpen" class="absolute bottom-0 left-0 w-full z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur shadow-sm pb-[env(safe-area-inset-bottom)] px-4 py-6" @click.stop>
        <div class="flex items-center gap-3 mb-2">
          <!-- Prev Page Button -->
          <button class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0" @click="prevPage">
            <ChevronLeftIcon class="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>

          <span class="text-s text-gray-500 font-medium tabular-nums min-w-[1.5rem] text-right">{{ currentPage + 1 }}</span>

          <input
            v-model.number="currentPage"
            type="range"
            min="0"
            :max="totalPages - 1"
            step="1"
            class="flex-1 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer mx-2 accent-blue-600 dark:bg-gray-700 focus:outline-none"
            @mousedown="isDragging = true"
            @touchstart="isDragging = true"
            @mouseup="isDragging = false"
            @touchend="isDragging = false"
          >

          <span class="text-s text-gray-500 font-medium tabular-nums min-w-[1.5rem]">{{ totalPages }}</span>

          <!-- Next Page Button -->
          <button class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0" @click="nextPage">
            <ChevronRightIcon class="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
      </div>
    </transition>

    <!-- Content Area: Paging Mode -->
    <!-- Important: overflow-hidden on container, content moves via transform -->
    <div class="absolute inset-0 z-0 overflow-hidden">
      <div
        ref="contentRef"
        class="column-content h-screen w-screen [column-width:90vw] [column-fill:auto]"
        :style="contentTextStyle"
      >
        <div v-if="readerStore.loading" class="h-full w-full flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-current opacity-50" />
        </div>
        <template v-else>
          <!-- Title -->
          <h1 class="text-2xl font-bold mb-8 mt-4">
            {{ readerStore.currentChapter?.title }}
          </h1>
          <!-- Paragraphs -->
          <p v-for="(para, i) in paragraphs" :key="i" class="reader-paragraph" :style="{ marginBottom: `${margin}px` }">
            {{ para }}
          </p>
        </template>
      </div>
    </div>

    <!-- Drawers using Headless UI Dialog -->

    <!-- TOC Drawer -->
    <TransitionRoot as="template" :show="showTOC">
      <Dialog as="div" class="relative z-50" @close="showTOC = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/50 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-hidden z-10">
          <div class="absolute inset-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-x-0 bottom-0 flex max-h-[85vh]">
              <TransitionChild
                as="template"
                enter="transform transition ease-in-out duration-300"
                enter-from="translate-y-full"
                enter-to="translate-y-0"
                leave="transform transition ease-in-out duration-300"
                leave-from="translate-y-0"
                leave-to="translate-y-full"
              >
                <DialogPanel class="pointer-events-auto w-full bg-white dark:bg-gray-900 rounded-t-xl shadow-xl flex flex-col">
                  <ReaderTOC
                    :chapters="readerStore.chapters"
                    :current-chapter-index="readerStore.currentChapterIndex"
                    :has-book="!!readerStore.currentBook"
                    @jump-to-chapter="(i) => { loadChapter(i); showTOC = false }"
                  />
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Settings Drawer -->
    <TransitionRoot as="template" :show="showSettings">
      <Dialog as="div" class="relative z-50" @close="showSettings = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/25 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-hidden z-10">
          <div class="absolute inset-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-x-0 bottom-0 flex max-h-[75vh]">
              <TransitionChild
                as="template"
                enter="transform transition ease-in-out duration-300"
                enter-from="translate-y-full"
                enter-to="translate-y-0"
                leave="transform transition ease-in-out duration-300"
                leave-from="translate-y-0"
                leave-to="translate-y-full"
              >
                <DialogPanel class="pointer-events-auto w-full bg-white dark:bg-gray-800 rounded-t-xl shadow-xl">
                  <ReaderSettings />
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<style scoped>
.reader-paragraph {
  text-indent: 2em;
  text-align: justify;
  break-inside: auto; /* Allow breaking */
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
