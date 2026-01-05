<!-- markdownlint-disable MD033 MD036 MD041 -->
<div align="center">
  <!-- <img src="docs/assets/logo.png" alt="Glean Logo" width="120" height="120"> -->
  <h1>Glean (拾阅)</h1>
  <p><strong>轻量级的、自托管的个人小说云阅工具</strong></p>
  
  [![GitHub stars](https://img.shields.io/github/stars/ZiyuZ/Glean?style=for-the-badge)](https://github.com/ZiyuZ/Glean)
  [![GitHub forks](https://img.shields.io/github/forks/ZiyuZ/Glean?style=for-the-badge)](https://github.com/ZiyuZ/Glean)
</div>

> [!NOTE]
> **项目说明**：Glean 仍处于不定期维护中，功能开发主要以满足个人需求为主。部分功能（如多用户支持等）暂不在开发计划中。

## ✨ 核心特性

<table border="0">
  <tr>
    <td width="60%" valign="top">
      <ul>
        <li>📂 <b>智能扫描</b>：自动递归遍历服务器数据目录下的所有 TXT 文件，支持实时增量扫描。</li>
        <li>🔍 <b>搜索过滤</b>：支持书架书籍的关键字搜索，以及按阅读状态筛选。</li>
        <li>⚡️ <b>智能解析</b>：优化的正则表达式解析引擎，解决复杂中文语境下的误判。</li>
        <li>📚 <b>云端书架</b>：多端同步的阅读进度，自动保存最后一次阅读位置。</li>
        <li>📱 <b>原生级 PWA</b>：深度适配 iOS/Android 安全区域，支持沉浸式全屏阅读。</li>
        <li>🚀 <b>极致性能</b>：基于流式加载与章节预锁机制，秒开大文件，丝滑翻页。</li>
        <li>📖 <b>智能分页</b>：基于 CSS Columns 的精确分页算法，自动适配不同屏幕尺寸。</li>
        <li>🎨 <b>个性化设置</b>：支持字体、主题、亮度、动画开关等多项阅读配置。</li>
        <li>🎲 <b>发现功能</b>：随机从书库中抽取一本小说开启新旅程。</li>
        <li>🌟 <b>文件管理</b>：支持在线标星收藏，支持一键清库维护工具。</li>
        <li>🐳 <b>单容器部署</b>：开箱即用，生产环境单容器静态托管。</li>
      </ul>
    </td>
    <td width="40%" valign="center">
      <img src="assets/demo.gif" alt="Glean Demo" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />
    </td>
  </tr>
</table>

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目并进入目录**

   ```sh
   git clone https://github.com/ZiyuZ/Glean.git
   cd Glean
   ```

2. **添加书本**
   - 将书本放在 `data/books` 目录下
   - 书本必须是 txt 格式
   - 或者将 compose.yml 中的自定义挂载书籍目录取消注释并修改

3. **启动服务**
    - 如果没有 apps 这个 network，请在 compose.yml 中删除 networks 部分，否则启动会报错

   ```sh
   docker compose up -d
   ```

4. **访问应用**
   - 前端：<http://localhost:5959>
   - API 文档：<http://localhost:5959/docs>

### 方式二：开发环境

#### 前置要求

- Python 3.14+ 和 [uv](https://github.com/astral-sh/uv)
- [bun](https://bun.sh/)
- [just](https://github.com/casey/just)（可选，用于任务管理）

#### 启动步骤

1. **安装依赖**

   ```sh
   just install
   # 或手动执行：
   # cd backend && uv sync
   # cd frontend && bun install
   ```

2. **启动开发服务器**

   ```sh
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

> 通常情况下不需要修改

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
- **PWA**: 支持离线阅读已加载章节
- **Package Manager**: `bun` - 快速 JavaScript 运行时和包管理器

## 📂 项目结构

```sh
Glean/
├── assets/      # 项目资源 (如演示 GIF)
├── data/        # 数据根目录 (书籍、数据库)
├── backend/     # Python 后端 (FastAPI)
├── frontend/    # Vue 3 前端 (Vite)
├── Dockerfile   # 多阶段构建 (Frontend + Backend)
├── compose.yml  # Docker Compose 配置
└── justfile     # 任务运行器配置
```

> [!TIP]
> 更多详细的技术实现和模块说明，请参阅各个子目录下的 README：
>
> - [后端详细文档 (Backend Details)](backend/README.md)
> - [前端详细文档 (Frontend Details)](frontend/README.md)

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
- `eslint`: JavaScript 代码检查工具（通过 `bun run lint` 调用）

### 开发命令

项目使用 `just` 作为任务运行器：

```sh
# 后端开发
just dev-be      # 启动 FastAPI 开发服务器（带热重载）
just run-be      # 以生产模式启动服务器
just install-be  # 安装后端依赖

# 前端开发
just dev-fe      # 启动前端开发服务器
just build-fe    # 构建前端生产版本
just install-fe  # 安装前端依赖

# 组合命令
just install     # 安装所有依赖
just lint        # 格式化代码并修复 lint 问题
just dev         # 同时启动前后端开发服务器
just check       # 代码检查（格式化 + 构建测试）
```

## 🗺️ 路线图

- [ ] **简单身份认证**
  - 当前应用只支持单用户，并无支持多用户计划
  - 计划使用简单的密码认证
- [ ] **AI 增强**
  - [ ] **AI 文字清洗**：自动修复乱码、去除广告段落。
  - [ ] **AI 自动化标签**：根据内容自动生成分类标签。计算相似书籍，实现猜您喜欢。
  - [ ] **AI 标题规范化**：统一章节标题格式。
- [ ] **数据洞察**
  - [ ] 阅读热力图 (GitHub Style)
  - [ ] 年度阅读报告
  - [ ] 阅读速度分析及读完时间预测
- [ ] **开放生态**
  - [ ] 配合外部独立自动采集器，自动触发文件系统变化

## 💡 为什么选择 Glean？

与传统的 WebDAV 同步或整包下载阅读器不同，**Glean** 强调"服务端即本体"。你的所有书籍和阅读记录都留在服务器上，前端仅作为一个轻量级的窗口。无论你是在电脑、手机还是平板上，阅读体验都是连贯且无缝的。

---

<div align="center">
  <p>祝你在 <strong>Glean (拾阅)</strong> 的世界里享受纯粹的阅读时光！</p>
</div>
