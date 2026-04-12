from pathlib import Path

from loguru import logger

from .models import BookLine, ParsedChapter
from .utils import detect_encoding, ingest_fragments

MIN_LINES_FOR_REAL_CHAPTER = 5


def merge_soft_line_breaks(lines: list[BookLine]) -> list[BookLine]:
    """
    章内合并：调用方保证传入的是非空、已 strip 的正文片段。

    - 上一行以句末标点结尾：开启新段。
    - 否则：当前行拼接到上一段末尾。
    """
    if not lines:
        return []

    merged: list[BookLine] = []
    buffer = lines[0]

    for current in lines[1:]:
        if buffer.is_end():
            merged.append(buffer)
            buffer = current
        else:
            buffer = buffer.merge_with(current)

    merged.append(buffer)

    return merged


def parse_fragments_to_book(fragments: list[str], file_stem: str) -> list[ParsedChapter]:
    # 结果顺序固定为：卷前 + 正文章节。
    lines = [BookLine(fragment) for fragment in fragments]
    # 第0章是卷前，第1章开始是正文。
    chapter_candidates: list[ParsedChapter] = [ParsedChapter(title=file_stem, body_lines=[])]

    # 遍历每一行，根据是否是标题，创建新章节或拼接到当前章节。
    for line in lines:
        if line.is_title():  # 遇到标题时，创建新章节。
            chapter_candidates.append(ParsedChapter(title=line.normalized_title(), body_lines=[]))
        else:  # 遇到正文时，拼接到当前章节。
            chapter_candidates[-1].body_lines.append(line)

    # 短章并入上一章。从第1章开始，第0章是卷前
    folded_chapters = [chapter_candidates[0]]
    for chapter in chapter_candidates[1:]:
        if len(chapter.body_lines) < MIN_LINES_FOR_REAL_CHAPTER:
            folded_chapters[-1].body_lines.extend(chapter.body_lines)
        else:
            folded_chapters.append(chapter)

    # 合并软换行
    for chapter in folded_chapters:
        chapter.body_lines = merge_soft_line_breaks(chapter.body_lines)

    return folded_chapters


def parse_book(file_path: Path) -> list[ParsedChapter]:
    encoding = detect_encoding(file_path)
    try:
        raw = file_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        logger.warning(f'Failed to read {file_path} with {encoding}, retrying with gb18030')
        raw = file_path.read_text(encoding='gb18030', errors='strict')

    fragments = ingest_fragments(raw)
    if not fragments:
        raise ValueError('No content in file')

    logger.info(f'Parser summary | file={file_path.name} | fragments={len(fragments)}')
    return parse_fragments_to_book(fragments, file_path.stem)
