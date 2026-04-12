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
├── package.json              # 依赖与脚本
├── vite.config.ts            # Vite / PWA 等构建配置
├── public/                   # 静态资源（图标、Manifest 等，不经打包处理）
└── src/
    ├── main.ts               # 应用入口
    ├── App.vue               # 根组件
    ├── style.css             # 全局样式
    ├── vite-env.d.ts         # Vite 类型声明
    ├── api/                  # API 封装（基于 Ky 的 client 与各域请求）
    │   ├── client.ts         # HTTP 客户端实例与通用逻辑
    │   ├── index.ts          # 统一导出
    │   ├── books.ts
    │   ├── chapters.ts
    │   ├── scan.ts
    │   └── system.ts
    ├── assets/               # 随构建处理的静态资源
    │   └── vue.svg
    ├── components/
    │   ├── book/
    │   │   └── BookItem.vue  # 书架列表项
    │   ├── layout/           # 顶栏、底栏、PWA、服务不可用遮罩等
    │   │   ├── AppHeader.vue
    │   │   ├── BottomNav.vue
    │   │   ├── PWABadge.vue
    │   │   └── ServiceUnavailableOverlay.vue
    │   ├── library/          # 书库扫描与文件树
    │   │   ├── FileTree.vue
    │   │   ├── ScanManager.vue
    │   │   └── TreeItem.vue
    │   ├── reader/           # 阅读器设置与目录
    │   │   ├── ReaderSettings.vue
    │   │   └── ReaderTOC.vue
    │   └── ui/               # 通用弹窗、空态、骨架屏等
    │       ├── BaseModal.vue
    │       ├── ConfirmModal.vue
    │       ├── EmptyState.vue
    │       └── SkeletonLoader.vue
    ├── composables/
    │   └── useReader.ts      # 阅读器相关组合式逻辑
    ├── router/
    │   └── index.ts          # 路由表
    ├── stores/               # Pinia：鉴权、书架、阅读器、系统状态
    │   ├── auth.ts
    │   ├── books.ts
    │   ├── reader.ts
    │   └── system.ts
    ├── types/
    │   └── api.ts            # 与后端契约相关的 TS 类型
    └── views/                # 页面级视图
        ├── Bookshelf.vue     # 书架首页
        ├── Discovery.vue     # 发现 / 随机推荐
        ├── Library.vue       # 书库与扫描管理
        ├── Login.vue         # 登录（后端开启密码时）
        └── Reader.vue        # 阅读页
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

### 登录页 (Login) - `/login`

**展示形式**：全屏玻璃拟态风格登录框（当后端开启 `APP_PASSWORD` 后自动跳转）。

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

## API 约定

前端统一通过 `src/api/` 下的请求函数访问后端，并默认使用 `/api` 前缀。

### 接口分组

- 书籍：列表、详情、进度同步、标星、单本删除、批量删除
- 章节：章节目录、章节正文
- 扫描：启动扫描、查询状态、停止扫描
- 系统：登录、鉴权状态、健康检查、版本信息

### 接口文档

- 运行后端后访问 `/docs`（Swagger / OpenAPI）获取最新参数与响应定义
- 代码中的调用示例可参考 `src/api/*.ts`

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
