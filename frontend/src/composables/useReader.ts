import { useLocalStorage } from '@vueuse/core'
import { computed } from 'vue'

/**
 * 阅读器配置
 */
export interface ReaderConfig {
  fontSize: number // 字体大小（px）
  lineHeight: number // 行高（倍数）
  theme: 'light' | 'dark' | 'sepia' | 'night' // 主题
  brightness: number // 亮度（0-100）
  paddingX: number // 水平边距
  paddingY: number // 垂直边距
  margin: number // 段落间距（px）
  enableAnimation: boolean // 是否开启翻页动画
}

const defaultConfig: ReaderConfig = {
  fontSize: 18,
  lineHeight: 1.8,
  theme: 'light',
  brightness: 100,
  paddingX: 12,
  paddingY: 10,
  margin: 16, // 段落间距
  enableAnimation: true,
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

  /* Split Padding */
  const paddingX = computed({
    get: () => config.value.paddingX ?? 2,
    set: v => config.value.paddingX = v,
  })

  const paddingY = computed({
    get: () => config.value.paddingY ?? 10,
    set: v => config.value.paddingY = v,
  })

  const enableAnimation = computed({
    get: () => config.value.enableAnimation ?? true,
    set: v => config.value.enableAnimation = v,
  })

  const margin = computed({
    get: () => config.value.margin ?? 16,
    set: v => config.value.margin = v,
  })

  return {
    config,
    fontSize,
    lineHeight,
    theme,
    brightness,
    paddingX,
    paddingY,
    margin,
    enableAnimation,
  }
}
