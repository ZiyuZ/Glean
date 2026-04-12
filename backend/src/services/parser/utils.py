import hashlib
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from typing import override

from charset_normalizer import from_path
from loguru import logger
from opencc_purepy import OpenCC

_OPENCC = OpenCC('t2s')
_FULL_TO_HALF_TRANS = str.maketrans(
    '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ「」',
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""',
)
_SYMBOL_TRANS = str.maketrans(
    ',.:;?!',
    '，。：；？！',
)
_URL_RE = re.compile(
    r'(?:https?://|www\.)[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]+'
    r'|\b[a-z0-9][a-z0-9.-]{1,253}\.(?:com|net|org|edu|gov|cn|cc|tw|hk|us|in|info|pro|xyz|club|work|space|top|site|online|io)(?:/[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]*)?'
    r'|(?:/[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]*)?\b[A-Za-z0-9._-]+\.(?:php|asp|aspx|jsp|cgi|do)(?:\?[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]*)?',
    re.IGNORECASE,
)


def detect_encoding(file_path: Path) -> str:
    """
    检测文件编码。

    检测失败时回退到 gb18030。
    """
    result = from_path(file_path).best()
    if result is None or result.encoding is None:
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

    parser = HTMLTextExtractor()
    parser.feed(content)
    return ''.join(parser.result)


def ingest_fragments(raw: str) -> list[str]:
    """
    读取阶段：不涉及软换行合并。HTML、换行统一、全文 URL、NFKC、全半角、繁简，
    再 split('\\n') 并去掉空行，得到待打标与分桶的正文碎片序列。
    """
    text = raw.replace('\r\n', '\n').replace('\r', '\n')  # 统一换行符
    text = clean_html(text)  # 去除 HTML 标签
    text = _URL_RE.sub('', text)  # 全文去 URL，再切行
    text = unicodedata.normalize('NFKC', text)  # 规范化 Unicode 字符
    text = _OPENCC.convert(text)  # 繁简转换
    text = text.translate(_FULL_TO_HALF_TRANS)  # 全角转半角
    text = text.translate(_SYMBOL_TRANS)  # 标点符号转换
    return [s for line in text.split('\n') if (s := line.strip())]
