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
- 📱 **流式阅读**：前端仅加载当前阅读章节，节省流量且性能卓越，完美适配移动端点击交互。
- 🚀 **单容器部署**：开发环境分离，生产环境单容器静态托管，部署简单。

## 🛠️ 技术栈

### 后端 (Python)

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [PyDantic](https://pydantic.dev/) - 异步高性能 API
- **Database**: [SQLite](https://www.sqlite.org/) + [SQLModel](https://sqlmodel.tiangolo.com/) - 轻量级存储元数据与进度
- **Parser**: 基于正则表达式与字节偏移量的流式解析器
- **Utility**: `chardet` (编码检测), `watchdog` (目录监听)
- **Package Manager**: `uv` - 快速 Python 包管理

### 前端 (Vue)

- **Framework**: [Vue 3 (Vite)](https://cn.vuejs.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Package Manager**: `bun` - 快速 JavaScript 运行时和包管理器
- **PWA**: 支持离线阅读已加载章节

## 📂 项目结构

```text
glean/
├── data/                   # 数据目录（根目录）
│   ├── books/              # 存放书籍的物理目录
│   └── database.db         # 数据库文件
├── backend/                # Python 后端 (FastAPI)
│   ├── main.py             # FastAPI 应用入口
│   ├── pyproject.toml      # 项目配置和依赖 (uv)
│   └── src/
│       ├── api/            # API 路由模块
│       └── core/           # 核心模块（配置、模型）
├── frontend/               # Vue 3 前端 (Vite)
│   ├── src/
│   │   ├── components/     # 阅读器、书架组件
│   │   ├── views/          # 首页、发现页、阅读页
│   │   └── store/          # Pinia 状态管理
│   └── dist/              # 构建产物（生产环境）
├── Dockerfile              # 多阶段构建（前端+后端）
├── compose.yml             # Docker Compose 配置
├── justfile                # 任务运行器配置
└── .env                    # 环境变量配置（可选）
```

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目并进入目录**

   ```bash
   git clone <repository-url>
   cd glean
   ```

2. **配置环境变量（可选）**

   ```bash
   cp env.example .env
   # 编辑 .env 文件，设置 DATA_DIR（默认使用 ./data）
   ```

3. **启动服务**

   ```bash
   docker compose up -d
   ```

4. **访问应用**
   - 前端：<http://localhost:8000>
   - API 文档：<http://localhost:8000/docs>

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

应用使用 `pydantic-settings` 管理配置，支持通过环境变量或 `.env` 文件配置。

**配置数据目录环境变量：**

- `DATA_DIR`: 数据根目录路径（默认：`./data`）

**自动计算路径：**

- 书籍目录：`${DATA_DIR}/books`
- 数据库路径：`${DATA_DIR}/database.db`

**配置方式：**

1. **使用 `.env` 文件（推荐）**

   ```env
   # 项目根目录创建 .env 文件
   DATA_DIR=./data
   ```

2. **环境变量**

   ```bash
   export DATA_DIR=/path/to/data
   ```

3. **Docker Compose**

   ```yaml
   # compose.yml 会自动从 .env 读取，或使用默认值
   environment:
     - DATA_DIR=${DATA_DIR:-/app/data}
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

### 多阶段构建流程

1. **Stage 1 (frontend-builder)**：使用 `oven/bun:1` 构建前端
2. **Stage 2 (runtime)**：使用 `ghcr.io/astral-sh/uv:python3.14-alpine` 运行后端
3. 前端构建产物复制到后端工作目录的 `frontend/dist`

## 📝 开发指南

### 开发工具

- `uv`: Python 包管理器和项目管理工具，替代 pip/poetry
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

### API 设计

所有 API 使用 `/api` 前缀，路由按功能模块拆分：

- **books.py**: 书籍相关 API
  - `GET /api/books` - 获取书架列表（含搜索、标星筛选）
  - `GET /api/books/random` - 随机获取一本书
  - `GET /api/books/{id}` - 获取书籍详情
  - `PATCH /api/books/{id}/progress` - 同步阅读进度（章节索引 + 字节偏移量）
  - `PATCH /api/books/{id}/star` - 标星/取消标星
  - `DELETE /api/books/{id}` - 从物理磁盘删除文件

- **chapters.py**: 章节相关 API
  - `GET /api/chapters/books/{id}/chapters` - 获取章节目录
  - `GET /api/chapters/books/{id}/content/{chapter_index}` - 获取特定章节的纯文本

- **scan.py**: 扫描 API
  - `POST /api/scan` - 手动触发全量/增量目录扫描

- **files.py**: 文件浏览 API
  - `GET /api/files?path=...` - 浏览文件系统目录

完整 API 文档：启动服务后访问 `/docs`

### 数据库模型设计

**Book (书籍模型)** - `src/core/models.py`

- `id`: 主键
- `hash_id`: 文件内容哈希（用于去重和变更检测）
- `title`: 书名
- `path`: 文件路径
- `is_starred`: 是否标星
- `last_read_time`: 最后阅读时间
- `file_size`: 文件大小（字节）
- `file_mtime`: 文件最后修改时间（Unix 时间戳）
- `encoding`: 文件编码（缓存，避免重复检测）
- `chapter_index`: 当前阅读的章节索引
- `chapter_offset`: 在章节内的字节偏移量
- `chapters`: 关联的章节列表（一对多关系）

**Chapter (章节模型)** - `src/core/models.py`

- `id`: 主键
- `book_id`: 所属书籍 ID（外键）
- `title`: 章节标题
- `order_index`: 章节序号
- `start_byte`: 章节在文件中的起始字节偏移量
- `end_byte`: 章节在文件中的结束字节偏移量
- `book`: 关联的书籍（多对一关系）

**设计要点：**

- **单用户场景**：阅读进度直接存储在 `Book` 模型中，无需额外的用户表
- **字节偏移量**：使用字节偏移量而非行号，支持多编码文件且性能更好
- **文件元数据缓存**：`file_size` 和 `file_mtime` 用于快速判断文件是否变更，避免每次都计算哈希

### 核心逻辑实现要点

**章节自动切分逻辑**

为了实现"点击即读"，后端不应在请求时才解析，而应在**扫描书籍**时完成索引。

- **思路**：记录每个章节标题在 TXT 文件中的 **字节偏移量 (Byte Offset)**
- **优点**：数据库只存 `(章名, 起始位, 结束位)`。读取时利用 `file.seek()` 直接跳到对应位置，性能极高，内存占用极小

**发现页 (Random Discovery)**

- **思路**：后端提供一个 `GET /books/random` 接口，从数据库中随机选一条记录返回

**文件管理**

- **物理删除**：接口调用 `Path.unlink()`。需注意权限控制，防止误删系统文件

## ⚠️ 注意事项

1. **路径安全 (Path Traversal)**：在处理物理文件删除或读取时，务必校验文件名，不要让用户通过 `../` 访问到你 `data/` 目录之外的文件。
2. **大文件解析性能**：如果 TXT 超过 50MB，正则匹配会慢。建议使用流式读取（`readline`）来扫描章节标记，而不是一次性 `f.read()`。
3. **多编码兼容**：中文 TXT 常见 GB18030 或者 GBK 编码。读取前先用 `chardet` 采样前 1024 字节判断编码，否则会出现乱码。
4. **移动端体验**：Web 端阅读器最怕的是"浏览器顶栏/底栏"闪现。建议在前端使用 `fullscreen API` 提供沉浸式体验。
5. **进度保存频率**：不要每次滚动都发请求。只有在**切换章节**或**每隔 30 秒**或**页面关闭前 (onbeforeunload)** 同步进度。

## 💡 为什么选择 Glean？

与传统的 WebDAV 同步或整包下载阅读器不同，**Glean** 强调"服务端即本体"。你的所有书籍和阅读记录都留在服务器上，前端仅作为一个轻量级的窗口。无论你是在电脑、手机还是平板上，阅读体验都是连贯且无缝的。

祝你在 **Glean (拾阅)** 的世界里享受纯粹的阅读时光！
