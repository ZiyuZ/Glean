# 项目设计文档：Cloud-Novel-Reader

## 1. 项目结构设计 (Project Structure)

建议采用前后端分离的目录结构，方便在 Vibe/Cursor 中进行模块化开发。

```text
glean/
├── data/                   # 数据目录（根目录）
│   ├── books/             # 存放书籍的物理目录
│   └── database.db        # SQLite 数据库文件
├── backend/                # Python 后端 (FastAPI)
│   ├── main.py             # FastAPI 应用入口
│   ├── pyproject.toml      # 项目配置和依赖 (uv)
│   ├── uv.lock             # 依赖锁定文件
│   └── src/
│       ├── api/            # API 路由模块
│       │   ├── __init__.py # 路由汇总
│       │   ├── books.py    # 书籍相关 API
│       │   ├── chapters.py # 章节相关 API
│       │   ├── scan.py     # 扫描 API
│       │   └── files.py    # 文件浏览 API
│       └── core/           # 核心模块
│           ├── __init__.py
│           ├── config.py   # 配置管理（支持环境变量）
│           └── models.py   # 数据库模型 (SQLModel)
├── frontend/               # Vue 前端 (Vite + Vue 3)
│   ├── src/
│   │   ├── api/            # 请求封装
│   │   ├── components/     # 阅读器、书架组件
│   │   ├── views/          # 首页、发现页、阅读页
│   │   └── store/          # Pinia (存储阅读进度、设置)
│   ├── tailwind.config.js  # 样式配置
│   └── package.json
├── justfile                # 任务运行器配置
└── docker-compose.yml      # 可选：方便一键部署
```

## 2. 开发基本思路与技术栈

### 后端 (Python + FastAPI + SQLModel + PyDantic)

> 使用 uv 管理依赖，使用 Python 3.14

* **开发工具：**
* `uv`: Python 包管理器和项目管理工具，替代 pip/poetry
* `just`: 任务运行器，用于统一管理开发命令（见 `justfile`）
* `ruff`: 代码格式化和 lint 工具（通过 `uv tool run ruff` 调用）

* **核心库：**
* `FastAPI`: 异步接口，性能好。
* `SQLModel`: 基于 SQLAlchemy 和 Pydantic 的 ORM，用于数据库模型定义。
* `SQLite`: 轻量级存储书籍元数据、章节索引、进度。
* `chardet`: 解决 TXT 乱码问题（检测 GBK/UTF-8）。
* `watchdog`: 监听 `data/` 目录变化，自动触发扫描（待实现）。
* `aiofiles`: 异步文件操作支持。

* **API 设计思路：**
* 所有 API 使用 `/api` 前缀
* 路由按功能模块拆分到 `src/api/` 目录下：
  * `books.py`: 书籍相关 API
    * `GET /api/books` - 获取书架列表（含搜索、标星筛选）
    * `GET /api/books/random` - 随机获取一本书
    * `GET /api/books/{id}` - 获取书籍详情
    * `PATCH /api/books/{id}/progress` - 同步阅读进度（章节索引 + 字节偏移量）
    * `PATCH /api/books/{id}/star` - 标星/取消标星
    * `DELETE /api/books/{id}` - 从物理磁盘删除文件
  * `chapters.py`: 章节相关 API
    * `GET /api/chapters/books/{id}/chapters` - 获取章节目录
    * `GET /api/chapters/books/{id}/content/{chapter_index}` - 获取特定章节的纯文本
  * `scan.py`: 扫描 API
    * `POST /api/scan` - 手动触发全量/增量目录扫描
  * `files.py`: 文件浏览 API
    * `GET /api/files?path=...` - 浏览文件系统目录

### 前端 (Vue 3 + Vite + Tailwind CSS + PWA)

> 使用 bun 管理依赖，使用 `vite-plugin-pwa` 为项目配置 PWA 功能。要求配置 `runtimeCaching` 策略，使得所有来自 `/api/chapters/` 的请求都能被缓存，以支持离线阅读已加载的章节。

* **核心库：**
* `Ky`: 请求后端 API。
* `Pinia`: 管理全局状态（如当前书籍 ID、字体大小、背景主题）。
* `Vue Router`: 路由跳转。

* **阅读器界面思路：**
* **虚拟滚动/动态渲染：** 不要一次性加载整本书，只请求当前章节。
* **分区点击区：** 使用透明层覆盖，监听 `click` 位置。

## 3. 数据库模型设计

### 模型结构

* **Book (书籍模型)** - `src/core/models.py`
  * `id`: 主键
  * `hash_id`: 文件内容哈希（用于去重和变更检测）
  * `title`: 书名
  * `path`: 文件路径
  * `is_starred`: 是否标星
  * `last_read_time`: 最后阅读时间
  * `file_size`: 文件大小（字节）
  * `file_mtime`: 文件最后修改时间（Unix 时间戳）
  * `encoding`: 文件编码（缓存，避免重复检测）
  * `chapter_index`: 当前阅读的章节索引
  * `chapter_offset`: 在章节内的字节偏移量
  * `chapters`: 关联的章节列表（一对多关系）

* **Chapter (章节模型)** - `src/core/models.py`
  * `id`: 主键
  * `book_id`: 所属书籍 ID（外键）
  * `title`: 章节标题
  * `order_index`: 章节序号
  * `start_byte`: 章节在文件中的起始字节偏移量
  * `end_byte`: 章节在文件中的结束字节偏移量
  * `book`: 关联的书籍（多对一关系）

### 设计要点

* **单用户场景**：阅读进度直接存储在 `Book` 模型中，无需额外的用户表
* **字节偏移量**：使用字节偏移量而非行号，支持多编码文件且性能更好
* **文件元数据缓存**：`file_size` 和 `file_mtime` 用于快速判断文件是否变更，避免每次都计算哈希

## 4. 核心逻辑实现要点

### A. 章节自动切分逻辑 (后端的难点)

为了实现“点击即读”，后端不应在请求时才解析，而应在**扫描书籍**时完成索引。

* **思路：** 记录每个章节标题在 TXT 文件中的 **字节偏移量 (Byte Offset)**。
* **优点：** 数据库只存 `(章名, 起始位, 结束位)`。读取时利用 `file.seek()` 直接跳到对应位置，性能极高，内存占用极小。

### B. 发现页 (Random Discovery)

* **思路：** 后端提供一个 `GET /books/random` 接口，从数据库中随机选一条记录返回。

### C. 文件管理

* **物理删除：** 接口调用 `Path.unlink()`。需注意权限控制，防止误删系统文件。

## 5. 配置管理

### 环境变量配置

应用使用 `pydantic-settings` 管理配置，支持通过环境变量覆盖默认值。

**默认配置：**
* 数据目录：`项目根目录/data`
* 书籍目录：`data/books`
* 数据库路径：`data/database.db`

**环境变量：**
* `DATA_DIR`: 数据根目录路径（绝对路径或相对于项目根目录）
* `BOOKS_DIR`: 书籍存放目录（相对于 DATA_DIR 或绝对路径）
* `DATABASE_PATH`: 数据库文件路径（相对于 DATA_DIR 或绝对路径）

**`.env` 文件位置：**
* **推荐位置**：项目根目录（`glean/.env`）- 这样前后端可以共享配置
* **备选位置**：`backend/.env` - 如果只想在后端使用
* 系统会按顺序查找这两个位置，找到第一个就使用
* 优先级：环境变量 > 项目根目录 `.env` > `backend/.env` > 默认值

**使用示例：**

1. **开发环境（使用默认值）：**

   ```bash
   # 无需配置，直接使用默认路径
   just dev-be
   ```

2. **通过 `.env` 文件配置（推荐）：**
   在项目根目录创建 `.env` 文件：

   ```env
   DATA_DIR=./data
   BOOKS_DIR=books
   DATABASE_PATH=database.db
   ```

3. **通过环境变量配置：**

   ```bash
   # Windows PowerShell
   $env:DATA_DIR="D:\my-books"
   $env:BOOKS_DIR="novels"
   $env:DATABASE_PATH="db.sqlite"
   just dev-be
   
   # Linux/Mac
   export DATA_DIR="/app/data"
   export BOOKS_DIR="/app/data/books"
   export DATABASE_PATH="/app/data/database.db"
   just dev-be
   ```

4. **Docker Compose 配置：**

   ```yaml
   services:
     backend:
       environment:
         - DATA_DIR=/app/data
         - BOOKS_DIR=/app/data/books
         - DATABASE_PATH=/app/data/database.db
       volumes:
         - ./data:/app/data
   ```

**注意事项：**
* 配置在应用启动时自动解析并确保目录存在
* 路径支持相对路径和绝对路径
* 相对路径会基于项目根目录或 `DATA_DIR` 解析

## 6. 开发命令参考

项目使用 `just` 作为任务运行器，常用命令：

* **后端开发：**
  * `just dev-be` - 启动 FastAPI 开发服务器（带热重载）
  * `just run-be` - 以生产模式启动服务器
  * `just lint` - 格式化代码并修复 lint 问题
  * `just install-be` - 安装后端依赖

* **前端开发：**
  * `just dev-fe` - 启动前端开发服务器
  * `just build-fe` - 构建前端生产版本
  * `just install-fe` - 安装前端依赖

* **组合命令：**
  * `just dev` - 同时启动前后端开发服务器
  * `just install` - 安装所有依赖
  * `just check` - 代码检查（格式化 + 构建测试）

## 7. 注意事项 (坑位预警)

1. **路径安全 (Path Traversal)：** * 在处理物理文件删除或读取时，务必校验文件名，不要让用户通过 `../` 访问到你 `data/` 目录之外的文件。
2. **大文件解析性能：**
    * 如果 TXT 超过 50MB，正则匹配会慢。建议使用流式读取（`readline`）来扫描章节标记，而不是一次性 `f.read()`。
3. **多编码兼容：**
    * 中文 TXT 常见 GBK 编码。读取前先用 `chardet` 采样前 1024 字节判断编码，否则全是乱码。
4. **移动端体验：**
    * Web 端阅读器最怕的是“浏览器顶栏/底栏”闪现。建议在前端使用 `fullscreen API` 提供沉浸式体验。
5. **进度保存频率：**
    * 不要每次滚动都发请求。建议在**切换章节**或**每隔 30 秒**或**页面关闭前 (onbeforeunload)** 同步进度。
