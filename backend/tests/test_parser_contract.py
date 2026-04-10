import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.parser import parse_book  # ty: ignore[unresolved-import]


def _write_book(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding='utf-8')
    return path


def test_parse_book_returns_parse_result(tmp_path: Path):
    book_path = _write_book(
        tmp_path,
        'v2.txt',
        '\n'.join(['第一章 开始', '正文1', '正文2', '正文3', '正文4', '正文5']),
    )
    result = parse_book(book_path)

    assert result.chapters
    assert result.stats.total_lines > 0
    assert any(chapter.title == '第一章 开始' for chapter in result.chapters)


def test_parse_book_empty_file_raises(tmp_path: Path):
    book_path = _write_book(tmp_path, 'empty.txt', '')
    with pytest.raises(ValueError, match='No content in file'):
        parse_book(book_path)
