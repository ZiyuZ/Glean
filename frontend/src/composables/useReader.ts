/**
 * 阅读器相关的组合式函数
 * 使用 @vueuse/core 提供的工具
 */

import { computed, type Ref } from 'vue'
import { useScroll, useFullscreen, useLocalStorage } from '@vueuse/core'

/**
 * 阅读器配置
 */
export interface ReaderConfig {
    fontSize: number // 字体大小（px）
    lineHeight: number // 行高（倍数）
    theme: 'light' | 'dark' | 'sepia' | 'night' // 主题
    brightness: number // 亮度（0-100）
}

const defaultConfig: ReaderConfig = {
    fontSize: 18,
    lineHeight: 1.8,
    theme: 'light',
    brightness: 100,
}

/**
 * 使用阅读器配置
 */
export function useReaderConfig() {
    const config = useLocalStorage<ReaderConfig>('reader-config', defaultConfig)

    const fontSize = computed({
        get: () => config.value.fontSize,
        set: (value) => {
            config.value.fontSize = value
        },
    })

    const lineHeight = computed({
        get: () => config.value.lineHeight,
        set: (value) => {
            config.value.lineHeight = value
        },
    })

    const theme = computed({
        get: () => config.value.theme,
        set: (value) => {
            config.value.theme = value
        },
    })

    const brightness = computed({
        get: () => config.value.brightness,
        set: (value) => {
            config.value.brightness = value
        },
    })

    return {
        config,
        fontSize,
        lineHeight,
        theme,
        brightness,
    }
}

/**
 * 使用滚动控制
 */
export function useReaderScroll(containerRef: Ref<HTMLElement | null>) {
    const { x, y, isScrolling, arrivedState, directions } = useScroll(containerRef)

    const isAtTop = computed(() => arrivedState.top)
    const isAtBottom = computed(() => arrivedState.bottom)
    const isScrollingUp = computed(() => directions.top)
    const isScrollingDown = computed(() => directions.bottom)

    return {
        scrollX: x,
        scrollY: y,
        isScrolling,
        isAtTop,
        isAtBottom,
        isScrollingUp,
        isScrollingDown,
    }
}

/**
 * 使用全屏
 */
export function useReaderFullscreen(targetRef?: Ref<HTMLElement | null>) {
    const { isFullscreen, enter, exit, toggle } = useFullscreen(targetRef)

    return {
        isFullscreen,
        enterFullscreen: enter,
        exitFullscreen: exit,
        toggleFullscreen: toggle,
    }
}

