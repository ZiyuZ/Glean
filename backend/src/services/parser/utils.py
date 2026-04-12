import hashlib
from html.parser import HTMLParser
from pathlib import Path
from typing import override

from charset_normalizer import from_path
from loguru import logger


def detect_encoding(file_path: Path) -> str:
    """
    检测文件编码

    使用 chardet 检测文件编码
    返回编码名称（如 'utf-8', 'gb18030'）
    """
    result = from_path(file_path).best()
    if result is None:
        logger.warning(f'Failed to detect encoding for {file_path}, using default encoding gb18030')
        return 'gb18030'
    return result.encoding


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
