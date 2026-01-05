import re
from pathlib import Path
from typing import TypedDict

from loguru import logger

from .cleaner import clean_content
from .utils import detect_encoding
from .validator import is_line_chapter_title


class ChapterDict(TypedDict):
    title: str
    order_index: int
    content: list[str]


def parse_chapters(file_path: Path) -> list[ChapterDict]:
    """
    基于行扫描的章节解析逻辑
    """
    # 1. 读取并清洗 (自动检测编码)
    encoding = detect_encoding(file_path)
    try:
        raw_content = file_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        # Fallback to gb18030 if detection failed or was wrong
        logger.warning(f'Failed to read {file_path} with {encoding}, retrying with gb18030')
        raw_content = file_path.read_text(encoding='gb18030', errors='strict')

    content = clean_content(raw_content)

    # 2. 拆分为非空行
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    if not lines:
        raise ValueError(f'No content in file: {file_path}')

    # 3. 扫描章节
    # 结构: [ {'title': str, 'content': str} ]
    # 初始章节（前言/默认章节）
    raw_chapters: list[ChapterDict] = [ChapterDict(title=file_path.stem, order_index=-1, content=[])]

    for line in lines:
        if is_line_chapter_title(line):
            # 发现新章节
            raw_chapters.append(
                ChapterDict(
                    # 将章节名里的 ASCII 符号转换为空格并去掉头尾空格
                    title=re.sub(
                        r'[^\u4e00-\u9fffA-Za-z0-9 ]',
                        ' ',
                        line,
                    ).strip(),
                    order_index=-1,
                    content=[],
                )
            )
        else:
            # 是正文，归属到当前章节
            # 直接拼接字符串 (用户要求)
            if raw_chapters[-1]['content']:
                raw_chapters[-1]['content'].append(line)
            else:
                raw_chapters[-1]['content'] = [line]

    # 4. 后处理：合并空章节
    merged_chapters: list[ChapterDict] = []

    for i, chapter in enumerate(raw_chapters):
        if i == 0:
            merged_chapters.append(chapter)
            continue

        # 检查当前章节是否为空（或者内容非常少，可能是误判的标题）
        # 这里判断空字符串即可，因为上面只有 append line
        if not chapter['content']:
            # 空章节 -> 标题回退为正文
            # 追加到 上一个章节(merged_chapters[-1]) 的末尾
            if merged_chapters[-1]['content']:
                merged_chapters[-1]['content'].append('\n\n' + chapter['title'])
            else:
                merged_chapters[-1]['content'].append(chapter['title'])
        else:
            merged_chapters.append(chapter)

    # 5. 计算 order_index
    for i, chapter in enumerate(merged_chapters):
        chapter['order_index'] = i

    logger.info(f'Parsed {len(merged_chapters)} chapters from {file_path}')
    return merged_chapters
