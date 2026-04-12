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
    # Keys: preamble (-1), 第一章 (line index 0), 第三章 (line index 9); 第二章 误判 因正文过短被并入 preamble
    assert len(result) == 3
    assert set(result.keys()) == {-1, 0, 9}
    assert result[0].title == '第一章 开场'
    assert result[0].body_lines[-1].text == 'a5'
    assert [line.text for line in result[-1].body_lines] == ['短1', '短2']
    assert result[9].title == '第三章 正文'


def test_pipeline_idempotent_same_input(tmp_path: Path, monkeypatch):
    book_path = _write_book(
        tmp_path,
        'stable.txt',
        '\n'.join(['第一章', '正文1', '正文2', '正文3', '正文4', '正文5']),
    )
    monkeypatch.setenv('PARSER_RULES_ENABLED', '0')
    first = parse_book(book_path)
    second = parse_book(book_path)

    first_text = {k: [line.text for line in ch.body_lines] for k, ch in first.items()}
    second_text = {k: [line.text for line in ch.body_lines] for k, ch in second.items()}
    assert [ch.title for ch in first.values()] == [ch.title for ch in second.values()]
    assert first_text == second_text
