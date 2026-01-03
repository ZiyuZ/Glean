import { computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'

/**
 * 阅读器配置
 */
export interface ReaderConfig {
    fontSize: number // 字体大小（px）
    lineHeight: number // 行高（倍数）
    theme: 'light' | 'dark' | 'sepia' | 'night' // 主题
    brightness: number // 亮度（0-100）
    padding: number // 内容边距（px）
    margin: number // 段落间距（px）
}

const defaultConfig: ReaderConfig = {
    fontSize: 18,
    lineHeight: 1.8,
    theme: 'light',
    brightness: 100,
    padding: 64, // px-6 py-8 = 48px + 32px
    margin: 16, // 段落间距
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

    const padding = computed({
        get: () => config.value.padding,
        set: (value) => {
            config.value.padding = value
        },
    })

    const margin = computed({
        get: () => config.value.margin,
        set: (value) => {
            config.value.margin = value
        },
    })

    return {
        config,
        fontSize,
        lineHeight,
        theme,
        brightness,
        padding,
        margin,
    }
}

