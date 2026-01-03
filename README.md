<!-- markdownlint-disable MD036 -->
# Glean (拾阅) 📖

> **Glean (拾阅)** 是一款轻量级的、自托管的个人小说云阅工具。
> 采用"云端解析 + 流式加载"架构，旨在将你的私有 TXT 藏书库转化为一个体验优异的 Web 阅读平台。

## ✨ 核心特性

- 📂 **智能扫描**：自动递归遍历服务器数据目录下的所有 TXT 文件，支持实时增量扫描。
- 🔍 **章节切分**：基于正则表达式的智能解析引擎，自动提取章节目录，实现秒开大文件。
- 📚 **云端书架**：多端同步的阅读进度，自动保存最后一次阅读位置，点开即读。
- 🎲 **发现功能**：打破"选择困难症"，随机从书库中抽取一本小说开启新旅程。
- 🌟 **文件管理**：支持在线标星收藏，支持直接从物理磁盘彻底删除文件。
- 📱 **移动端适配**：响应式布局，完美适配移动端点击和触摸交互。
- 📖 **智能分页**：基于 CSS Columns 的精确分页算法，自动适配不同屏幕尺寸，提供精美的翻页体验。
- 🎨 **个性化设置**：支持字体大小、行高、主题、亮度、边距、动画开关等多项阅读配置。
- 🚀 **单容器部署**：开发环境分离，生产环境单容器静态托管，部署简单。

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目并进入目录**

   ```bash
   git clone <repository-url>
   cd glean
   ```

2. **启动服务**

   ```bash
   docker compose up -d
   ```

3. **访问应用**
   - 前端：<http://localhost:5959>
   - API 文档：<http://localhost:5959/docs>

### 方式二：开发环境

#### 前置要求

- Python 3.14+ 和 [uv](https://github.com/astral-sh/uv)
- [bun](https://bun.sh/)
- [just](https://github.com/casey/just)（可选，用于任务管理）

#### 启动步骤

1. **安装依赖**

   ```bash
   just install
   # 或手动执行：
   # cd backend && uv sync
   # cd frontend && bun install
   ```

2. **启动开发服务器**

   ```bash
   just dev
   # 或手动执行：
   # 终端1: just dev-be  (后端: http://localhost:8000)
   # 终端2: just dev-fe  (前端: http://localhost:5173)
   ```

3. **访问应用**
   - 前端开发服务器：<http://localhost:5173>
   - 后端 API：<http://localhost:8000>
   - API 文档：<http://localhost:8000/docs>

## ⚙️ 配置说明

### 环境变量

应用使用 `pydantic-settings` 管理配置。

- `APP_ENV`：运行环境，Docker 镜像默认 `production`，本地默认 `development`。
- `DATA_DIR`：数据根目录（默认：项目根目录下的 `data`，容器内默认 `/app/data`）。

**自动计算路径：**

- 书籍目录：`${DATA_DIR}/books`
- 数据库路径：`${DATA_DIR}/database.db`

## 🛠️ 技术栈

### 后端 (Python)

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [PyDantic](https://pydantic.dev/) - 异步高性能 API
- **Database**: [SQLite](https://www.sqlite.org/) + [SQLModel](https://sqlmodel.tiangolo.com/) - 轻量级存储元数据与进度
- **Parser**: 基于正则表达式与字符偏移量的流式解析器
- **Package Manager**: `uv` - Python 包管理

### 前端 (Vue)

- **Framework**: [Vue 3 (Vite)](https://cn.vuejs.org/) - 组合式 API，响应式系统
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- **State Management**: [Pinia](https://pinia.vuejs.org/) - Vue 官方状态管理
- **Router**: [Vue Router](https://router.vuejs.org/) - 官方路由管理器
- **Icons**: [Heroicons](https://heroicons.com/) - Tailwind CSS 官方图标库
- **Utilities**: [VueUse](https://vueuse.org/) - Vue 组合式工具集
- **Package Manager**: `bun` - 快速 JavaScript 运行时和包管理器
- **PWA**: 支持离线阅读已加载章节

## 📂 项目结构

```sh
glean/
├── data/                   # 数据目录（根目录）
│   ├── books/              # 存放书籍的物理目录
│   └── database.db         # 数据库文件
├── backend/                # Python 后端 (FastAPI)
│   ├── main.py             # FastAPI 应用入口
│   ├── pyproject.toml      # 项目配置和依赖 (uv)
│   ├── README.md           # 后端详细文档
│   └── src/
│       ├── api/            # API 路由模块
│       ├── core/           # 核心模块（配置、模型、数据库）
│       └── services/       # 业务逻辑层（解析、扫描、书籍服务）
├── frontend/               # Vue 3 前端 (Vite)
│   ├── src/
│   │   ├── components/     # 组件
│   │   │   ├── reader/     # 阅读器相关组件（Header, TOC, Settings, Content）
│   │   │   └── BottomNav.vue # 底部导航
│   │   ├── views/          # 页面视图（Bookshelf, Discovery, Settings, Reader）
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── composables/    # 组合式函数（useReader）
│   │   ├── api/            # API 客户端
│   │   └── types/          # TypeScript 类型定义
│   ├── README.md           # 前端详细文档
│   └── dist/             # 构建产物（生产环境）
├── Dockerfile              # 多阶段构建（前端+后端）
├── compose.yml             # Docker Compose 配置
├── justfile                # 任务运行器配置
└── .env                    # 环境变量配置（可选）
```

## 🏗️ 架构设计

### 开发环境 vs 生产环境

**开发环境：**

- 前后端分离运行
- 前端：Vite 开发服务器（`http://localhost:5173`）
- 后端：FastAPI 开发服务器（`http://localhost:8000`）
- Vite 代理：`/api` 请求代理到后端
- CORS：启用，允许前端跨域访问

**生产环境（Docker）：**

- 单容器部署：前端构建产物打包到后端容器
- 静态文件托管：FastAPI 挂载 `frontend/dist` 目录
- SPA 路由支持：Catch-all 路由返回 `index.html`
- 同源访问：前后端同源，无需 CORS

### 构建流程

1. **Stage 1 (frontend-builder)**：使用 `oven/bun:1` 构建前端
2. **Stage 2 (runtime)**：使用 `ghcr.io/astral-sh/uv:python3.14-alpine` 运行后端
3. 前端构建产物复制到后端工作目录的 `frontend/dist`

## 📝 开发指南

### 开发工具

- `uv`: Python 包管理器和项目管理工具，替代 pip/poetry
- `bun`: JavaScript 运行时和包管理器
- `just`: 任务运行器，用于统一管理开发命令（见 `justfile`）
- `ruff`: 代码格式化和 lint 工具（通过 `uv tool run ruff` 调用）

### 开发命令

项目使用 `just` 作为任务运行器：

```bash
# 后端开发
just dev-be      # 启动 FastAPI 开发服务器（带热重载）
just run-be      # 以生产模式启动服务器
just lint        # 格式化代码并修复 lint 问题
just install-be  # 安装后端依赖

# 前端开发
just dev-fe      # 启动前端开发服务器
just build-fe    # 构建前端生产版本
just install-fe  # 安装前端依赖

# 组合命令
just dev         # 同时启动前后端开发服务器
just install     # 安装所有依赖
just check       # 代码检查（格式化 + 构建测试）
```

### 详细文档

- **后端文档**：查看 [backend/README.md](backend/README.md)
  - API 设计
  - 数据库模型
  - 服务层架构
  - 开发指南

- **前端文档**：查看 [frontend/README.md](frontend/README.md)
  - 页面设计
  - 组件架构
  - PWA 配置
  - 开发指南

## 📋 功能状态

### ✅ 已完成

- [x] 书籍扫描和解析
- [x] 章节提取和流式加载
- [x] 阅读进度保存和恢复
- [x] 书架页面（显示有进度的书籍）
- [x] 发现页面（随机推荐书籍）
- [x] 阅读器界面（平滑翻页、设置面板、目录侧边栏）
- [x] 个性化配置（字体、行高、主题、亮度、边距、动画）
- [x] 目录导航
- [x] 触摸和点击交互
- [x] 标星收藏功能
- [x] 分页算法精度优化（当前可显示约 4/5 内容）

### 📋 未完成

- [ ] 书架按照最近阅读排序
  - 小于 1 天显示 X 小时 前，小于 1 小时显示 X 分钟前，小于 1 分钟显示刚刚
- [ ] 删除功能实现
  - 从书架删除和从库删除
- [ ] 书籍列表管理
  - 分文件夹 (树形管理)
  - 分页
  - 搜索
- [ ] 书架搜索
- [ ] 书架过滤
  - 收藏(标星) - 已实现
  - 已读完
  - 未读完 (有进度但没结束, 默认)
- [ ] 页内进度上传
- [ ] 页内进度条拖动
- [ ] PWA
  - 安卓状态栏主题色同步
  - 安卓底部安全边界导致可以往下滚动
  - 苹果 Header Padding Top
  - 章节预载和离线阅读
- [ ] 分章算法优化 (第二节课XXXXX,  XXXX是第一回XXXX)
- [ ] AI
  - AI 文字清洗
  - AI Tag
  - AI 标题规范化
- [ ] 其他 UI
  - 发现页换一批按钮放到 Header 上
  - 全局 Header, 阅读页隐藏
  - 清空数据库重新扫描

## 💡 为什么选择 Glean？

与传统的 WebDAV 同步或整包下载阅读器不同，**Glean** 强调"服务端即本体"。你的所有书籍和阅读记录都留在服务器上，前端仅作为一个轻量级的窗口。无论你是在电脑、手机还是平板上，阅读体验都是连贯且无缝的。

祝你在 **Glean (拾阅)** 的世界里享受纯粹的阅读时光！
