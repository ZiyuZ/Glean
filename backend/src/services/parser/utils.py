import hashlib
from html.parser import HTMLParser
from pathlib import Path
from typing import override

from chardet import detect
from loguru import logger


def detect_encoding(file_path: Path) -> str:
    """
    检测文件编码

    使用 chardet 检测文件编码
    返回编码名称（如 'utf-8', 'gb18030'）

    注意：charset-normalizer 在某些文件上可能返回 None，因此使用 chardet
    """
    # 读取前 1024 字节进行检测（对于大文件更高效）
    with open(file_path, 'rb') as f:
        sample = f.read(1024)

    result = detect(sample)
    encoding = result.get('encoding', None)
    # 如果检测失败，默认使用 gb18030（常见的中文编码）
    if not encoding:
        logger.warning(f'Failed to detect encoding for {file_path}, using default encoding gb18030')
        encoding = 'gb18030'
    # 统一处理 GB2312 -> GB18030
    if encoding.lower() == 'gb2312':
        encoding = 'gb18030'
    return encoding.lower()


def calculate_file_hash(file_path: Path) -> str:
    """
    计算文件内容的 MD5 哈希值

    用于检测文件是否被修改
    """
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        # 分块读取，避免大文件占用过多内存
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def clean_html(content: str) -> str:
    """去除 HTML 标签，提取纯文本（供读取与归一化使用）。"""

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.result: list[str] = []

        @override
        def handle_data(self, data: str):
            self.result.append(data)

        def get_text(self) -> str:
            return ''.join(self.result)

    parser = HTMLTextExtractor()
    parser.feed(content)
    return parser.get_text()
