// eslint.config.js
import antfu from '@antfu/eslint-config'

export default antfu({
  // 这里可以开启或关闭功能
  vue: true,
  typescript: true,
  // 可以在这里写你的自定义规则
  rules: {
    'no-console': 'warn',
  },
})
