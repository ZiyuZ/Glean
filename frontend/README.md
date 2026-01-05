<!-- markdownlint-disable MD036 -->
# Glean 前端文档

## 技术栈

- **Framework**: [Vue 3](https://cn.vuejs.org/) (Composition API, `<script setup>`)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **PWA**: [vite-plugin-pwa](https://vite-pwa-org.netlify.app/)
- **Package Manager**: [bun](https://bun.sh/)

## 项目结构

```sh
frontend/
├── src/
│   ├── api/                  # API 客户端 (axios 实例及请求函数)
│   ├── components/           # 组件
│   │   ├── reader/           # 阅读器专有组件 (Header, Settings, etc.)
│   │   ├── BookItem.vue      # 书架书籍条目
│   │   ├── BottomNav.vue     # 底部导航栏
│   │   ├── FileTree.vue      # 文件系统浏览器
│   │   └── ScanManager.vue   # 扫描任务管理
│   ├── views/                # 页面视图
│   │   ├── Bookshelf.vue     # 书架首页
│   │   ├── Discovery.vue     # 发现页 (随机推荐)
│   │   ├── Library.vue       # 库页 (文件系统扫描)
│   │   └── Reader.vue        # 阅读器核心页
│   ├── stores/               # Pinia 状态管理
│   ├── composables/          # 组合式函数 (逻辑复用)
│   ├── types/                # TypeScript 类型定义
│   ├── App.vue               # 根组件
│   ├── main.ts               # 入口文件
│   └── sw.ts                 # Service Worker (PWA)
├── public/                   # 静态资源 (图标、Manifest)
├── vite.config.ts            # Vite 配置
└── package.json              # 依赖配置
```

## 核心架构

### 前后端协议

- **章节内容格式**：后端 API 返回 **纯文本 (Plain Text)** 格式
- **前端渲染**：前端动态转换为 `p` 标签进行渲染
- **API 代理**：开发环境使用 Vite 代理 `/api` 到后端

### 开发环境配置

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## 页面与路由设计

### 书架页 (Bookshelf) - `/`

**展示形式**：列表视图

**条目内容**：

- 书名、上次阅读章节、进度百分比、最后阅读时间、状态标签。

### 发现页 (Discovery) - `/discovery`

**功能**：随便看看，随机从书库中抽取书籍。

### 书库页 (Library) - `/library`

**功能**：

- **物理路径浏览**：支持层级目录跳转。
- **扫描管理**：触发目录扫描，查看扫描进度。

### 阅读器 (Reader) - `/reader/:bookId`

**核心逻辑**：

- **纯文本渲染**：从后端获取 `content`，在前端进行分页或滚动渲染。
- **进度同步**：自动保存阅读位置。

**字体选择**：使用美观的中文非衬线字体（如思源黑体、苹方等）

## 阅读器 3x3 九宫格交互设计

在阅读界面上层覆盖一个 `fixed` 定位的透明网格层（Z-index 较高）：

| | 左 | 中 | 右 |
| ---: | :--- | :--- | :--- |
| **上** | (↑) 上一页 | (↑) 上一页 | (↑) 上一页 |
| **中** | (↓) 下一页 | (x) 菜单 | (↓) 下一页 |
| **下** | (↓) 下一页 | (↓) 下一页 | (↓) 下一页 |

## PWA 标准与离线化支持

项目符合 PWA 规范，确保在移动端可添加至桌面并全屏运行。

### Service Worker 策略

使用 `vite-plugin-pwa` 配置：

- **CacheFirst**：对于静态资源（字体、图标、UI 框架代码）
- **NetworkFirst**：对于书籍列表和目录
- **离线预存**：当用户点开某本书时，SW 自动缓存当前章节及其后两章的纯文本 API 响应

## 设置面板 (SettingsPanel)

**功能**：

- **亮度调节**：系统级或叠加半透明黑层
- **字号调节**：12px - 32px 可调
- **背景主题**：明亮、护眼、纸张、深色
- **进度跳转**：`input range` 滑块，对应章节的百分比

## API 集成

### 书籍列表

```typescript
// GET /api/books?starred=true&search=关键词&finished=false
interface Book {
  id: number
  title: string
  chapter_index: number | null
  chapter_offset: number | null
  is_finished: boolean
  is_starred: boolean
  last_read_time: number | null
  // ... 其他字段
}
```

### 章节内容

```typescript
// GET /api/chapters/books/{id}/content/{chapter_index}
// 返回：Plain Text Response
```

### 进度同步

```typescript
// PATCH /api/books/{id}/progress
// 参数：{ chapter_index: number, chapter_offset: number }
```

### 扫描状态

```typescript
// GET /api/scan/status
interface ScanStatus {
  is_running: boolean
  files_scanned: number
  files_added: number
  files_updated: number
  total_files: number
  current_file: string
  error: string | null
}
```

## 开发指南

### 安装依赖

```sh
cd frontend
bun install
```

### 运行开发服务器

```sh
bun run dev
# 或使用 just
just dev-fe
```

### 构建生产版本

```sh
bun run build
# 或使用 just
just build-fe
```

### 代码检查

```sh
bun run lint
```
