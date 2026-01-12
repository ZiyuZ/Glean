# Retree (归卷) 📚

**Retree** 是一款书库分析工具，支持文件相似度检测和基于本地 LLM 的文件名标准化。通过语义嵌入技术自动发现重复或高度相似的文件。

## 🌟 核心特性

- **相似度检测**：基于 text2vec 语义嵌入，发现内容相似的文件
- **多种比较模式**：支持 doc-mean、chunk-max、chunk-min、chunk-mean 四种相似度计算方式
- **增量同步**：智能识别新增/删除文件，只计算增量嵌入
- **文件名标准化**：使用本地 LLM (Ollama) 智能清洗文件名
- **隐私安全**：全流程本地化处理，无需上传数据到云端

## 🛠️ 技术架构

- **嵌入模型**: [shibing624/text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese)
- **LLM 推理**: [Ollama](https://ollama.com/) (推荐模型: Qwen2.5)
- **开发语言**: Python 3.14
- **关键库**: `torch`, `sentence-transformers`, `typer`, `rich`, `opencc`, `chardet`

## 📁 项目结构

```text
retree/src/
├── main.py           # CLI 入口 (Typer)
├── config.py         # 配置常量
├── models.py         # 数据模型 (dataclass)
├── scanner.py        # 文件扫描与元数据管理
├── embedder.py       # 嵌入计算与缓存
├── similarity.py     # 相似度分析
└── title_plugin.py   # LLM 文件名标准化
```

## 🚀 快速开始

### 安装依赖

```bash
pip install torch sentence-transformers typer rich opencc chardet
```

### 命令行使用

```bash
# 进入项目目录
cd retree/app

# 1. 扫描文件元数据
uv run main.py scan

# 2. 计算嵌入向量
uv run main.py embed                    # 增量更新
uv run main.py embed --force            # 全量计算

# 3. 分析相似度
uv run main.py similar                  # 默认 doc-mean 模式
uv run main.py similar --mode chunk-max --threshold 0.9

# 4. 一键运行完整流程
uv run main.py run --threshold 0.85

# 5. 查看当前状态
uv run main.py status

# 6. 标准化文件名（需要 Ollama）
ollama run qwen2.5:3b-instruct          # 先启动 LLM
uv run main.py title
```

### 相似度模式说明

| 模式 | 说明 |
| ---- | ---- |
| `doc-mean` | 将文档所有分块嵌入平均后比较（默认） |
| `chunk-max` | 对应位置分块比较，取最大相似度 |
| `chunk-min` | 对应位置分块比较，取最小相似度 |
| `chunk-mean` | 对应位置分块比较，取平均相似度 |

## 📊 数据存储

所有数据存储在 `data/retree/` 目录：

- `metadata.json` - 文件元数据（路径、大小、修改时间）
- `embeddings_*.npz` - 嵌入向量缓存（文件名包含配置参数）
- `similarity.json` - 相似度分析结果

## 🐳 Docker 使用

### 构建镜像

```bash
docker compose build
```

### 运行命令

```bash
# 查看帮助
docker compose run --rm retree --help

# 一键运行完整流程
docker compose run --rm retree run --threshold 0.9

# 单独运行各步骤
docker compose run --rm retree scan
docker compose run --rm retree embed
docker compose run --rm retree similar --mode chunk-mean

# 查看状态
docker compose run --rm retree status
```

### 自定义数据目录

修改 `compose.yml` 中的 volumes 配置：

```yaml
volumes:
  - /your/books/path:/data/books:ro    # 书库目录（只读）
  - /your/output/path:/data/retree     # 输出目录
```

### 直接使用 docker run

```bash
docker run --rm \
  -v /path/to/books:/data/books:ro \
  -v /path/to/output:/data/retree \
  retree:latest run --threshold 0.9
```
