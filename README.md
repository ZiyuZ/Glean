# Glean (拾阅) 📖

> **Glean (拾阅)** 是一款轻量级的、自托管的个人小说云阅工具。
> 采用“云端解析 + 流式加载”架构，旨在将你的私有 TXT 藏书库转化为一个体验优异的 Web 阅读平台。

## ✨ 核心特性

- 📂 **智能扫描**：自动递归遍历服务器数据目录下的所有 TXT 文件，支持实时增量扫描。
- 🔍 **章节切分**：基于正则表达式的智能解析引擎，自动提取章节目录，实现秒开大文件。
- 📚 **云端书架**：多端同步的阅读进度，自动保存最后一次阅读位置，点开即读。
- 🎲 **发现功能**：打破“选择困难症”，随机从书库中抽取一本小说开启新旅程。
- 🌟 **文件管理**：支持在线标星收藏，支持直接从物理磁盘彻底删除文件。
- 📱 **流式阅读**：前端仅加载当前阅读章节，节省流量且性能卓越，完美适配移动端点击交互。

## 🛠️ 技术栈

### 后端 (Python)

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - 异步高性能 API。
- **Database**: [SQLite](https://www.sqlite.org/) - 轻量级存储元数据与进度。
- **Parser**: 基于正则表达式与字节偏移量的流式解析器。
- **Utility**: `chardet` (编码检测), `watchdog` (目录监听)。

### 前端 (Vue)

- **Framework**: [Vue 3 (Vite)](https://cn.vuejs.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Networking**: Axios

## 📂 项目结构

```text
glean/
├── backend/                # FastAPI 后端核心
│   ├── data/               # 你的 TXT 小说存放目录
│   ├── database/           # SQLite 数据库
│   ├── core/               # 解析引擎与逻辑类
│   └── main.py             # API 入口
├── frontend/               # Vue 3 前端界面
│   ├── src/
│   │   ├── components/     # 阅读器、书架组件
│   │   └── views/          # 首页、发现页、阅读页
│   └── index.html
└── docker-compose.yml      # 一键部署配置
```

## 🚀 快速开始

### 1. 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
# 修改配置文件中的数据目录路径
python main.py
```

### 2. 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 📝 开发计划 (Roadmap)

- [ ] 后端：实现基于字节偏移量的 TXT 章节解析逻辑。
- [ ] 后端：开发书架与阅读进度的 API 接口。
- [ ] 前端：构建支持三栏分区点击的阅读器界面。
- [ ] 前端：实现响应式书架与“发现页”逻辑。
- [ ] 进阶：支持 PWA，提供离线阅读能力。

## 💡 为什么选择 Glean？

与传统的 WebDAV 同步或整包下载阅读器不同，**Glean** 强调“服务端即本体”。你的所有书籍和阅读记录都留在服务器上，前端仅作为一个轻量级的窗口。无论你是在电脑、手机还是平板上，阅读体验都是连贯且无缝的。

祝你在 **Glean (拾阅)** 的世界里享受纯粹的阅读时光！
