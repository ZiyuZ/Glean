<!-- markdownlint-disable MD036 -->
# Glean 后端文档

## 技术栈

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic](https://pydantic.dev/) - 异步高性能 API
- **Database**: [SQLite](https://www.sqlite.org/) + [SQLModel](https://sqlmodel.tiangolo.com/) - 轻量级存储元数据与进度
- **Parser**: 基于正则表达式的章节解析器
- **Encoding Detection**: `chardet` - 编码检测
- **Text Processing**: `opencc` - 繁体转简体
- **Package Manager**: `uv` - 快速 Python 包管理

## 项目结构

```sh
backend/
├── main.py                 # FastAPI 应用入口
├── pyproject.toml          # 项目配置和依赖
└── src/
    ├── api/                # API 路由模块
    │   ├── books.py        # 书籍相关 API
    │   ├── chapters.py     # 章节相关 API
    │   └── scan.py         # 扫描相关 API
    ├── core/               # 核心模块
    │   ├── models.py       # 数据库模型
    │   ├── config.py       # 配置管理
    │   └── database.py     # 数据库连接和会话
    └── services/           # 业务逻辑层
        ├── parser.py       # 文件解析服务（编码检测、内容清洗、章节解析）
        ├── book_service.py # 书籍服务（创建/更新书籍）
        └── scanner.py      # 扫描服务（目录扫描）
```

## 数据库模型

### Book (书籍模型)

- `id`: 主键
- `hash_id`: 文件内容哈希（用于去重和变更检测）
- `title`: 书名
- `path`: 文件相对路径
- `is_starred`: 是否标星
- `last_read_time`: 最后阅读时间（Unix 时间戳）
- `file_size`: 文件大小（字节）
- `file_mtime`: 文件最后修改时间（Unix 时间戳）
- `chapter_index`: 当前阅读的章节索引（对应 Chapter.order_index）
- `chapter_offset`: 在章节内的字符偏移量（用于恢复阅读位置）
- `is_finished`: 是否已读完
- `chapters`: 关联的章节列表（一对多关系）

### Chapter (章节模型)

- `id`: 主键
- `book_id`: 所属书籍 ID（外键）
- `title`: 章节标题
- `order_index`: 章节序号（从 0 开始）
- `content`: 章节内容（UTF-8 编码的文本，不包含章节标题，已清洗）
- `book`: 关联的书籍（多对一关系）

## API 文档

所有 API 使用 `/api` 前缀，完整文档可在启动服务后访问 `/docs` 查看。

### 书籍 API (`/api/books`)

- `GET /api/books` - 获取书架列表
  - 查询参数：`starred` (bool), `search` (str), `finished` (bool)
- `GET /api/books/random` - 随机获取书籍
  - 查询参数：`count` (int, 1-100，默认 1) - 返回的书籍数量
- `GET /api/books/{id}` - 获取书籍详情
- `PATCH /api/books/{id}/progress` - 同步阅读进度
  - 参数：`chapter_index` (int), `chapter_offset` (int)
  - 自动判断并更新 `is_finished` 状态
- `PATCH /api/books/{id}/finish` - 手动标记为已读完/未读完
- `PATCH /api/books/{id}/star` - 标星/取消标星
- `POST /api/books/{id}/reparse` - 重新解析指定书籍
- `DELETE /api/books/{id}` - 从物理磁盘删除文件

### 章节 API (`/api/books/{book_id}/chapters`)

- `GET /api/books/{book_id}/chapters` - 获取章节目录
- `GET /api/books/{book_id}/chapters/{chapter_index}` - 获取特定章节的纯文本内容

### 扫描 API (`/api/scan`)

- `POST /api/scan` - 触发目录扫描
  - 查询参数：`full_scan` (bool, 默认 false)
  - 返回：扫描任务已启动
- `GET /api/scan/status` - 获取扫描进度（轮询）
  - 返回：`is_running`, `files_scanned`, `files_added`, `files_updated`, `total_files`, `current_file`, `error`
- `POST /api/scan/stop` - 停止正在进行的扫描

## 服务层设计

### Parser Service (`services/parser.py`)

**编码检测** (`detect_encoding`)

- 使用 `chardet` 检测文件编码
- 读取前 1024 字节进行检测（高效）
- 支持 GB18030、GBK、UTF-8 等常见编码

**文件标准化** (`normalize_file`)

- 检测编码、解码、转换为 UTF-8 并保存
- 只做编码转换，不清洗内容，保持原始内容不变

**内容清洗** (`clean_content`)

- 去除 HTML 标签
- 全角转半角（数字、字母、引号）
- 繁体转简体（使用 opencc）
- 清理多余换行（统一换行符、合并连续换行、恢复被拆分的句子）

**章节解析** (`parse_chapters`)

- 使用正则表达式匹配常见章节标题格式：
  - `第X章/节/回`（支持中文数字和阿拉伯数字，确保在行首或前面没有汉字）
  - `Chapter X`（必须在行首）
  - 数字开头（如 "1. 标题"）
- 解析时清洗章节内容
- 返回章节列表，包含标题、序号、内容（已清洗）

**文件哈希** (`calculate_file_hash`)

- 使用 MD5 计算文件内容哈希
- 用于检测文件是否被修改

### Book Service (`services/book_service.py`)

**创建/更新书籍** (`create_or_update_book`)

- 标准化文件（转换为 UTF-8）
- 计算哈希、解析章节
- 根据 `hash_id` 判断是新书还是已存在
- 根据 `file_size` 和 `file_mtime` 判断是否需要重新解析
- 返回 `(book, is_new)` 元组

**重新解析** (`reparse_book`)

- 删除旧章节，重新解析文件
- 用于手动触发重新解析

### Scanner Service (`services/scanner.py`)

**目录扫描** (`scan_directory`)

- 递归遍历 `books_dir` 下的所有 `.txt` 文件
- 支持增量扫描（通过 `file_size` 和 `file_mtime` 判断）
- 支持全量扫描（强制重新解析所有文件）
- 自动删除数据库中不存在的文件记录
- 异步执行，使用全局状态字典跟踪进度

**状态管理**

- 全局状态字典：`is_running`, `files_scanned`, `files_added`, `files_updated`, `total_files`, `current_file`, `error`
- 支持轮询查询进度
- 支持停止扫描

## 配置管理

使用 `pydantic-settings` 管理配置，支持环境变量和 `.env` 文件。

**环境变量：**

- `DATA_DIR`: 数据根目录路径（默认：`./data`）

**自动计算的路径：**

- 书籍目录：`${DATA_DIR}/books`
- 数据库路径：`${DATA_DIR}/database.db`

配置文件位置：项目根目录的 `.env` 文件。

## 开发指南

### 安装依赖

```bash
cd backend
uv sync
```

### 运行开发服务器

```bash
uv run fastapi dev main.py
# 或使用 just
just dev-be
```

### 代码格式化

```bash
uv tool run ruff format .
uv tool run ruff check --fix .
# 或使用 just
just lint
```

### 数据库初始化

数据库会在应用启动时自动初始化（`main.py` 中调用 `init_db()`）。

## 核心设计要点

### 文件处理流程

1. **标准化阶段**（扫描时）：
   - 检测编码 → 解码 → 转换为 UTF-8 并保存
   - 只做编码转换，内容不变

2. **解析阶段**（扫描时）：
   - 读取 UTF-8 文件 → 提取章节 → 清洗内容 → 存储到数据库
   - 清洗包括：HTML 标签去除、全角转半角、繁体转简体、换行处理

### 增量扫描

- 通过 `file_size` 和 `file_mtime` 快速判断文件是否修改
- 避免每次都计算哈希，提高扫描效率
- 支持全量扫描选项，强制重新解析

### 完成状态判断

- 自动判断：当前章节是最后一章，且偏移量接近末尾（剩余 < 5% 或 < 200字符）
- 手动标记：前端可调用 `/api/books/{id}/finish` 手动标记

### 章节内容存储

- 章节内容直接存储在数据库中（已清洗的 UTF-8 文本）
- 读取时无需文件 I/O，性能更好
- 支持复杂的编码和清洗逻辑，无需担心文件损坏

## 注意事项

1. **路径安全**：文件路径校验，防止路径遍历攻击
2. **大文件处理**：当前实现会读取整个文件到内存，超大文件（>100MB）可能需要优化
3. **编码兼容**：使用 `chardet` 检测编码，支持 GB18030、GBK 等中文编码
4. **并发安全**：SQLite 使用 `check_same_thread=False` 支持多线程访问
5. **文件修改**：扫描时会标准化文件（转换为 UTF-8），原始编码信息会丢失，但内容保持不变
