"""文件解析服务：编码检测、内容清洗和章节解析"""

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import override

import opencc
from chardet import detect
from loguru import logger

# 清洗相关常量
END_PUNCTUATIONS = '。？！；）》〉】』」﹄〕…—～﹏￥'  # 可能作为行末标点符号
FULL_TO_HALF = str.maketrans(
    '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ「」',
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""',
)
CHAPTER_NUMBER_LENGTH = 5  # 检测章节号长度阈值
NONE_TEXT_LENGTH = 10  # 检测书名或章节名长度阈值


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


def clean_html(content: str) -> str:
    """
    去除 HTML 标签，提取纯文本
    """

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


def clean_line_breaks(content: str) -> str:
    """
    清理多余的换行符

    逻辑：
    1. 如果一行以标点符号结尾，下一行应该换行
    2. 如果一行很短（可能是标题），应该换行
    3. 如果一行只有一个字符，不换行（可能是排版问题）
    """
    # 使用 splitlines() 而不是 split()，保留换行符信息
    lines = content.splitlines(keepends=False)
    if not lines:
        return content

    new_lines = [lines[0]]
    add_new_line = True

    for line in lines[1:]:
        if add_new_line:
            new_lines.append(line)
        else:
            # 合并到上一行，添加空格分隔
            new_lines[-1] += ' ' + line if line else line

        # 判断下一行是否应该换行
        if not line:
            # 空行，下一行应该换行
            add_new_line = True
        else:
            # 如果当前行以标点符号结尾，下一行应该换行
            add_new_line = line[-1] in END_PUNCTUATIONS

            # 如果当前行很短（可能是章节号或标题），应该换行
            if len(line) < CHAPTER_NUMBER_LENGTH:
                # 特殊情况：单字符不换行（可能是排版问题）
                if len(line) != 1:
                    new_lines[-1] += ' '
                add_new_line = False
            elif len(line) < NONE_TEXT_LENGTH:
                add_new_line = True

    return '\n\n'.join(new_lines)


def clean_content(content: str) -> str:
    """
    清洗文本内容

    执行以下清洗步骤：
    1. 去除 HTML 标签
    2. 全角转半角（数字、字母、引号）
    3. 繁体转简体
    4. 清理多余换行
    """
    # 1. 去除 HTML 标签
    content = clean_html(content)

    # 2. 全角转半角
    content = content.translate(FULL_TO_HALF)

    # 3. 繁体转简体
    converter = opencc.OpenCC('t2s.json')
    content = converter.convert(content)

    # 4. 清理多余换行
    content = clean_line_breaks(content)

    return content


def normalize_file(file_path: Path) -> None:
    """
    标准化文件：检测编码、解码、转换为 UTF-8 并保存

    只做编码转换，不清洗内容，保持原始内容不变
    """
    # 检测编码
    encoding = detect_encoding(file_path)

    # 读取并解码
    try:
        content_bytes = file_path.read_bytes()
        content = content_bytes.decode(encoding, errors='replace')
    except UnicodeDecodeError as e:
        logger.error(f'Failed to decode {file_path} with encoding {encoding}: {e}')
        raise

    # 转换为 UTF-8 并保存（覆盖原文件，但内容不变，只是编码转换）
    file_path.write_text(content, encoding='utf-8')

    logger.info(f'Normalized file {file_path}: {encoding} -> utf-8')


def parse_chapters(file_path: Path) -> list[dict]:
    """
    解析文件章节（文件应该已经是 UTF-8 编码）

    返回章节列表，每个章节包含：
    - title: 章节标题
    - order_index: 章节序号（从 0 开始）
    - content: 章节内容（不包含章节标题）

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
        # 数字开头（如 "1. 标题" 或 "一、标题"）
        r'^\d+[\.、]',
        r'^[一二三四五六七八九十]+[、.]',
    ]

    # 合并所有模式
    combined_pattern = '|'.join(f'({pattern})' for pattern in patterns)
    chapter_regex = re.compile(combined_pattern, re.IGNORECASE | re.MULTILINE)

    # 读取文件（已经是 UTF-8）
    content = file_path.read_text(encoding='utf-8')

    # 查找所有章节标题的位置
    matches = list(chapter_regex.finditer(content))

    if not matches:
        # 如果没有找到章节标题，将整个文件作为一章
        # 清洗内容
        cleaned_content = clean_content(content)
        chapters.append(
            {
                'title': file_path.stem,  # 使用文件名作为标题
                'order_index': 0,
                'content': cleaned_content,
            }
        )
        return chapters

    # 处理每个章节
    for i, match in enumerate(matches):
        title_start_pos = match.start()
        next_chapter_start_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        # 提取章节标题（从匹配位置到换行符）
        title_line_end_pos = content.find('\n', title_start_pos)
        if title_line_end_pos == -1:
            # 如果没有换行符，标题行就是到文件末尾
            title_line_end_pos = len(content)
        else:
            # 标题行结束位置是换行符之后（跳过换行符）
            title_line_end_pos += 1

        # 提取章节标题文本
        title_line = content[title_start_pos:title_line_end_pos].strip()
        # 清理标题（去除多余空白和换行符）
        title = re.sub(r'\s+', ' ', title_line).strip()

        # 提取章节内容（标题行之后，不包含标题）
        content_start_pos = title_line_end_pos
        chapter_content = content[content_start_pos:next_chapter_start_pos].strip()

        # 清洗章节内容（HTML、全角转半角、繁体转简体、清理换行）
        chapter_content = clean_content(chapter_content)

        chapters.append(
            {
                'title': title,
                'order_index': i,
                'content': chapter_content,
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
