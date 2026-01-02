# 项目设计文档：Cloud-Novel-Reader

## 1. 项目结构设计 (Project Structure)

建议采用前后端分离的目录结构，方便在 Vibe/Cursor 中进行模块化开发。

```text
cloud-novel-reader/
├── backend/                # Python 后端 (FastAPI)
│   ├── data/               # 存放书籍的物理目录
│   ├── database/           # SQLite 数据库文件
│   ├── models.py           # 数据库模型 (SQLAlchemy/SQLModel)
│   ├── parser.py           # TXT 解析核心逻辑 (正则、编码识别)
│   ├── main.py             # API 路由入口
│   └── requirements.txt    # 后端依赖
├── frontend/               # Vue 前端 (Vite + Vue 3)
│   ├── src/
│   │   ├── api/            # Axios 请求封装
│   │   ├── components/     # 阅读器、书架组件
│   │   ├── views/          # 首页、发现页、阅读页
│   │   └── store/          # Pinia (存储阅读进度、设置)
│   ├── tailwind.config.js  # 样式配置
│   └── package.json
└── docker-compose.yml      # 可选：方便一键部署
```

## 2. 开发基本思路与技术栈

### 后端 (Python + FastAPI + SQLModel + PyDantic)

> 使用 uv 管理依赖，使用 Python 3.14

* **核心库：**
* `FastAPI`: 异步接口，性能好。
* `SQLAlchemy` + `SQLite`: 轻量级存储书籍元数据、章节索引、进度。
* `chardet`: 解决 TXT 乱码问题（检测 GBK/UTF-8）。
* `watchdog`: 监听 `data/` 目录变化，自动触发扫描。

* **API 设计思路：**
* `GET /books`: 获取书架列表（含搜索、标星筛选）。
* `POST /scan`: 手动触发全量/增量目录扫描。
* `GET /books/{id}/chapters`: 获取章节目录。
* `GET /books/{id}/content/{chapter_index}`: 获取特定章节的纯文本。
* `PATCH /books/{id}/progress`: 同步阅读进度（章节索引 + 滚动位置）。
* `DELETE /books/{id}`: 从物理磁盘删除文件。

### 前端 (Vue 3 + Vite + Tailwind CSS + PWA)

> 使用 bun 管理依赖，使用 `vite-plugin-pwa` 为项目配置 PWA 功能。要求配置 `runtimeCaching` 策略，使得所有来自 `/api/chapters/` 的请求都能被缓存，以支持离线阅读已加载的章节。

* **核心库：**
* `Axios`: 请求后端 API。
* `Pinia`: 管理全局状态（如当前书籍 ID、字体大小、背景主题）。
* `Vue Router`: 路由跳转。

* **阅读器界面思路：**
* **虚拟滚动/动态渲染：** 不要一次性加载整本书，只请求当前章节。
* **分区点击区：** 使用透明层覆盖，监听 `click` 位置。

## 3. 核心逻辑实现要点

### A. 章节自动切分逻辑 (后端的难点)

为了实现“点击即读”，后端不应在请求时才解析，而应在**扫描书籍**时完成索引。

* **思路：** 记录每个章节标题在 TXT 文件中的 **字节偏移量 (Byte Offset)**。
* **优点：** 数据库只存 `(章名, 起始位, 结束位)`。读取时利用 `file.seek()` 直接跳到对应位置，性能极高，内存占用极小。

### B. 发现页 (Random Discovery)

* **思路：** 后端提供一个 `GET /books/random` 接口，从数据库中随机选一条记录返回。

### C. 文件管理

* **物理删除：** 接口调用 `Path.unlink()`。需注意权限控制，防止误删系统文件。

## 4. 注意事项 (坑位预警)

1. **路径安全 (Path Traversal)：** * 在处理物理文件删除或读取时，务必校验文件名，不要让用户通过 `../` 访问到你 `data/` 目录之外的文件。
2. **大文件解析性能：**
    * 如果 TXT 超过 50MB，正则匹配会慢。建议使用流式读取（`readline`）来扫描章节标记，而不是一次性 `f.read()`。
3. **多编码兼容：**
    * 中文 TXT 常见 GBK 编码。读取前先用 `chardet` 采样前 1024 字节判断编码，否则全是乱码。
4. **移动端体验：**
    * Web 端阅读器最怕的是“浏览器顶栏/底栏”闪现。建议在前端使用 `fullscreen API` 提供沉浸式体验。
5. **进度保存频率：**
    * 不要每次滚动都发请求。建议在**切换章节**或**每隔 30 秒**或**页面关闭前 (onbeforeunload)** 同步进度。
