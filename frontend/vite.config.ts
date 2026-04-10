import path from 'node:path'
import process from 'node:process'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

const buildTime = new Date().toISOString()
const buildVersion = process.env.npm_package_version || 'dev'

// https://vitejs.dev/config/
export default defineConfig({
  // 确保 base 路径正确，静态资源使用相对路径
  base: '/',
  define: {
    'import.meta.env.VITE_BUILD_TIME': JSON.stringify(buildTime),
    'import.meta.env.VITE_BUILD_VERSION': JSON.stringify(buildVersion),
  },
  plugins: [vue(), VitePWA({
    registerType: 'autoUpdate',
    injectRegister: 'auto',

    pwaAssets: {
      disabled: false,
      config: true,
    },

    manifest: {
      name: 'Glean 拾阅',
      short_name: 'Glean',
      description: 'Glean 拾阅',
      theme_color: '#FFFFFF',
      display: 'standalone',
      start_url: '/',
      scope: '/',
    },

    devOptions: {
      enabled: true,
      navigateFallback: 'index.html',
      suppressWarnings: true,
      type: 'module',
    },
    workbox: {
      cleanupOutdatedCaches: true,
      clientsClaim: true,
      skipWaiting: true,
      runtimeCaching: [
        {
          urlPattern: /^https?:\/\/.*\/api\/books\/\d+\/chapters\/\d+(\?.*)?$/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'reader-chapter-content-cache',
            expiration: {
              maxEntries: 300,
              maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
            },
            cacheableResponse: {
              statuses: [0, 200],
            },
          },
        },
        {
          urlPattern: /^https?:\/\/.*\/api\/system\/health(\?.*)?$/,
          handler: 'NetworkOnly',
        },
        {
          urlPattern: /^https?:\/\/.*\/api\/.*/,
          handler: 'NetworkOnly',
        },
      ],
    },
  })],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    allowedHosts: true,
    proxy: {
      // 将所有 /api 开头的请求代理到后端
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
