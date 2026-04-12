from pathlib import Path

from loguru import logger

from .models import LineRecord, ParsedChapter
from .rule_engine import engine
from .utils import clean_html, detect_encoding


def _read_file(file_path: Path) -> list[LineRecord]:
    encoding = detect_encoding(file_path)
    try:
        raw_content = file_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        logger.warning(f'Failed to read {file_path} with {encoding}, retrying with gb18030')
        raw_content = file_path.read_text(encoding='gb18030', errors='strict')

    content = clean_html(raw_content).replace('\r\n', '\n').replace('\r', '\n')
    raw_lines = [content for line in content.split('\n') if (content := line.strip())]
    return [LineRecord(line_no=idx, text=raw_line) for idx, raw_line in enumerate(raw_lines, start=1)]


def _build_chapters(
    lines: list[LineRecord],
    file_path: Path,
    min_lines_for_real_chapter: int = 5,
) -> dict[int, ParsedChapter]:
    chapters: dict[int, ParsedChapter] = {-1: ParsedChapter(title=file_path.stem, body_lines=[])}
    current_chapter_key = -1

    for i, line in enumerate(lines):
        if line.is_title():
            chapters[i] = ParsedChapter(
                title=line.sanitized_chapter_title(),
                body_lines=[],
            )
            current_chapter_key = i
            continue

        chapters[current_chapter_key].body_lines.append(line)

    short_chapter_keys: list[int] = []
    for i, chapter in chapters.items():
        if i == -1:
            continue
        if len(chapter.body_lines) < min_lines_for_real_chapter:
            short_chapter_keys.append(i)

    for chapter_key in short_chapter_keys:
        merged_chapter = chapters.pop(chapter_key)
        chapters[-1].body_lines.extend(merged_chapter.body_lines)

    return chapters


def parse_book(file_path: Path) -> dict[int, ParsedChapter]:
    """
    统一解析入口：
    1) 读取与归一化
    2) 行分类（标题/正文/空行）
    3) 构建章节并修复异常短章节
    """
    lines = _read_file(file_path)
    if not lines:
        raise ValueError('No content in file')

    chapters = _build_chapters(lines, file_path)

    logger.info(f'Parser summary | file={file_path.name} | lines={len(lines)}')
    return chapters


def sanitize_chapter_body(body: str) -> tuple[str, int]:
    """Apply parser rules to chapter body."""
    paragraphs = [segment.strip() for segment in body.split('\n\n') if segment.strip()]
    lines = [LineRecord(line_no=idx, text=text) for idx, text in enumerate(paragraphs, start=1)]
    chapters = {0: ParsedChapter(title='runtime', body_lines=lines)}
    rule_hits = engine.apply(chapters)
    return chapters[0].to_body(), rule_hits
