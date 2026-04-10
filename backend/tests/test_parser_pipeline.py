import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.parser import parse_book  # ty: ignore[unresolved-import]


def _write_book(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding='utf-8')
    return path


def test_pipeline_chapter_detection_and_repair(tmp_path: Path):
    book_path = _write_book(
        tmp_path,
        'pipeline.txt',
        '\n'.join(
            [
                '第一章 开场',
                'a1',
                'a2',
                'a3',
                'a4',
                'a5',
                '第二章 误判',
                '短1',
                '短2',
                '第三章 正文',
                'b1',
                'b2',
                'b3',
                'b4',
                'b5',
            ]
        ),
    )

    result = parse_book(book_path)
    assert len(result.chapters) == 3
    assert result.chapters[1].title == '第一章 开场'
    assert result.chapters[1].body_lines[-1].normalized_text == '第二章 误判'
    assert result.stats.repaired_chapters == 1


def test_pipeline_idempotent_same_input(tmp_path: Path, monkeypatch):
    book_path = _write_book(
        tmp_path,
        'stable.txt',
        '\n'.join(['第一章', '正文1', '正文2', '正文3', '正文4', '正文5']),
    )
    monkeypatch.setenv('PARSER_RULES_ENABLED', '0')
    first = parse_book(book_path)
    second = parse_book(book_path)

    first_text = [[line.normalized_text for line in chapter.body_lines] for chapter in first.chapters]
    second_text = [[line.normalized_text for line in chapter.body_lines] for chapter in second.chapters]
    assert [chapter.title for chapter in first.chapters] == [chapter.title for chapter in second.chapters]
    assert first_text == second_text
