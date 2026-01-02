"""文件解析服务：编码检测和章节解析"""

import hashlib
import re
from pathlib import Path

from charset_normalizer import detect


def detect_encoding(file_path: Path) -> str:
    """
    检测文件编码

    使用 charset_normalizer 检测文件编码
    返回编码名称（如 'utf-8', 'gb18030'）
    """
    # 读取前 1024 字节进行检测（对于大文件更高效）
    with open(file_path, 'rb') as f:
        sample = f.read(1024)

    result = detect(sample)
    encoding = result.get('encoding', 'utf-8')

    # 如果检测失败，默认使用 utf-8
    if not encoding:
        encoding = 'utf-8'

    return encoding.lower()


def parse_chapters(file_path: Path, encoding: str) -> list[dict]:
    """
    解析文件章节

    返回章节列表，每个章节包含：
    - title: 章节标题
    - order_index: 章节序号（从 0 开始）
    - start_byte: 章节起始字节偏移量
    - end_byte: 章节结束字节偏移量

    使用正则表达式匹配常见的章节标题格式
    """
    chapters = []

    # 常见的章节标题正则模式
    patterns = [
        # 第X章/节/回（支持中文数字和阿拉伯数字）
        r'第[一二三四五六七八九十百千万\d]+[章节回]',
        # Chapter X 或 Chapter X: Title
        r'Chapter\s+\d+',
        # 第X章（纯数字）
        r'第\d+章',
        # 第X节
        r'第\d+节',
        # 第X回
        r'第\d+回',
        # 数字开头（如 "1. 标题" 或 "一、标题"）
        r'^\d+[\.、]',
        r'^[一二三四五六七八九十]+[、.]',
    ]

    # 合并所有模式
    combined_pattern = '|'.join(f'({pattern})' for pattern in patterns)
    chapter_regex = re.compile(combined_pattern, re.IGNORECASE | re.MULTILINE)

    with open(file_path, 'rb') as f:
        content_bytes = f.read()
        content = content_bytes.decode(encoding, errors='ignore')

    # 查找所有章节标题的位置
    matches = list(chapter_regex.finditer(content))

    if not matches:
        # 如果没有找到章节标题，将整个文件作为一章
        chapters.append(
            {
                'title': Path(file_path).stem,  # 使用文件名作为标题
                'order_index': 0,
                'start_byte': 0,
                'end_byte': len(content_bytes),
            }
        )
        return chapters

    # 处理每个章节
    for i, match in enumerate(matches):
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        # 提取章节标题（包含匹配的文本及后续文本直到换行）
        title_line = content[start_pos:end_pos].split('\n')[0].strip()
        # 清理标题（去除多余空白）
        title = re.sub(r'\s+', ' ', title_line).strip()

        # 计算字节偏移量
        # 需要将字符位置转换为字节位置
        start_byte = len(content[:start_pos].encode(encoding))
        end_byte = len(content[:end_pos].encode(encoding)) if i + 1 < len(matches) else len(content_bytes)

        chapters.append(
            {
                'title': title,
                'order_index': i,
                'start_byte': start_byte,
                'end_byte': end_byte,
            }
        )

    return chapters


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
