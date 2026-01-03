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
│   ├── components/           # 组件
│   │   ├── Reader.vue        # 阅读器组件
│   │   ├── Bookshelf.vue     # 书架组件
│   │   └── SettingsPanel.vue # 设置面板
│   ├── views/                # 页面视图
│   │   ├── Home.vue          # 书架页
│   │   ├── Discovery.vue     # 发现与文件库页
│   │   └── ReaderView.vue    # 阅读器页
│   ├── store/                # Pinia 状态管理
│   │   ├── books.ts          # 书籍状态
│   │   └── reader.ts         # 阅读器状态
│   ├── App.vue               # 根组件
│   ├── main.ts               # 入口文件
│   ├── style.css             # 全局样式
│   └── sw.ts                 # Service Worker
├── public/                   # 静态资源
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

**展示形式**：简明的列表视图

**条目内容**：

- 书名
- 上次阅读章节
- 阅读进度百分比（右侧）
- 最后一次阅读时间
- 标星状态
- 是否已读完

**交互**：

- 点击：直接进入阅读器对应的历史位置
- 长按/右键：调出"删除/标星"菜单
- 筛选：支持按标星、搜索、是否读完筛选

### 发现与文件库 (Discovery) - `/discovery`

**功能**：

- **物理路径浏览**：支持层级目录跳转
- **随机功能**：顶部提供"随便看看 (Random)"入口
- **文件管理**：每个文件条目旁有"标星"和"删除"图标

**API 调用**：

- `GET /api/files?path=...` - 浏览文件系统目录
- `GET /api/books/random` - 随机获取一本书

### 阅读器 (Reader) - `/reader/:id`

**核心逻辑**：

- **纯文本渲染**：从后端获取 `content`，在前端进行排版
- **无缝滚动**：支持点击翻页与平滑滚动
- **预取逻辑**：当前章节读完 80% 时，静默请求下一章缓存
- **进度同步**：切换章节或每隔 30 秒同步进度

**字体选择**：使用美观的中文非衬线字体（如思源黑体、苹方等）

## 阅读器 3x3 九宫格交互设计

在阅读界面上层覆盖一个 `fixed` 定位的透明网格层（Z-index 较高）：

| 左 | 中 | 右 |
| :--- | :--- | :--- |
| (0,0) 返回上一页 | (1,0) 返回上一页 | (2,0) 下一页 |
| (0,1) 下一页 | (1,1) 弹出设置菜单 | (2,1) 下一页 |
| (0,2) 下一页 | (1,2) 下一页 | (2,2) 下一页 |

**逻辑细节**：

- **(0,0)**: `router.back()` 返回上一页
- **(1,1)**: 切换 `showSettingsPanel` 状态
- **其他 7 个区域**: 触发 `nextPage` 逻辑（向下滚动一个屏幕高度或加载下一章）

## PWA 标准与离线化支持

项目符合 PWA 规范，确保在移动端可添加至桌面并全屏运行。

### Service Worker 策略

使用 `vite-plugin-pwa` 配置：

- **CacheFirst**：对于静态资源（字体、图标、UI 框架代码）
- **NetworkFirst**：对于书籍列表和目录
- **离线预存**：当用户点开某本书时，SW 自动缓存当前章节及其后两章的纯文本 API 响应

### 清单文件 (manifest.json)

- `display: fullscreen` - 去除浏览器地址栏
- `orientation: portrait-primary` - 锁定竖屏（可选）
- `theme_color`: 主题色

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

```bash
cd frontend
bun install
```

### 运行开发服务器

```bash
bun run dev
# 或使用 just
just dev-fe
```

### 构建生产版本

```bash
bun run build
# 或使用 just
just build-fe
```

### 代码检查

```bash
bun run lint
```

## 交互动画建议

- **页面切换**：使用 `Vue Transition` 的 `fade` 效果
- **设置面板**：从底部向上滑出 (`translate-y`)
- **侧边文件目录**：从左侧滑出
- **章节切换**：平滑滚动或淡入淡出

## 注意事项

1. **进度保存频率**：不要每次滚动都发请求，只在切换章节、每隔 30 秒或页面关闭前同步
2. **移动端体验**：使用 `fullscreen API` 提供沉浸式体验，避免浏览器顶栏/底栏闪现
3. **离线支持**：合理使用 Service Worker 缓存策略，确保离线时能阅读已加载章节
4. **性能优化**：章节内容按需加载，预取下一章内容
