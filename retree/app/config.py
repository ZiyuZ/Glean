"""配置文件"""

from pathlib import Path

# 路径配置
RETREE_ROOT = Path(__file__).parent.parent
GLEAN_ROOT = RETREE_ROOT.parent
DATA_ROOT = GLEAN_ROOT / 'data'
BOOKS_ROOT = DATA_ROOT / 'books'

# retree 数据存储目录
RETREE_DATA = DATA_ROOT / 'retree'
RETREE_DATA.mkdir(exist_ok=True)

# 数据文件路径
METADATA_FILE = RETREE_DATA / 'metadata.json'
SIMILARITY_FILE = RETREE_DATA / 'similarity.json'

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {'.txt', '.txty'}

# LLM 配置（标题标准化插件）
OLLAMA_URL = 'http://localhost:11434/api/generate'
LLM_MODEL = 'qwen3:4b-instruct'
LLM_TIMEOUT = 30

TITLE_PROMPT_TEMPLATE = """\
你是一个文件名标准化助手。将给定的书籍文件名规范化，只返回标准化后的书名。

返回 JSON 格式（不要 markdown 代码块）：
{"standardized": "<标准化书名>"}

规则：
1. 去掉作者名（除非是作品集标题如"刘慈欣作品集"）
2. 去掉版本信息：全集、完整版、校对版、修订版、完结等
3. 去掉网站/水印：[起点]、【知轩藏书】、网址等
4. 去掉多余符号：书名号、方括号，统一括号格式
5. 保留重要信息：系列名、卷号、续集标识等
6. 非文学标题（如网页帖子）直接返回原名

文件名：{{filename}}
"""
