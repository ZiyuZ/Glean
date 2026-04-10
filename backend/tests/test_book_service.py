import sys
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from core.models import Chapter  # ty: ignore[unresolved-import]
from services.book_service import create_or_update_book  # ty: ignore[unresolved-import]


def test_create_or_update_book_persists_chapter_body(tmp_path: Path):
    books_dir = tmp_path / 'books'
    books_dir.mkdir(parents=True, exist_ok=True)
    source = books_dir / 'sample.txt'
    source.write_text(
        '\n'.join(['第一章 开始', '正文1', '正文2', '正文3', '正文4', '正文5']),
        encoding='utf-8',
    )

    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        book, _ = create_or_update_book(
            session=session,
            file_path=source,
            books_dir=books_dir,
            force_reparse=True,
        )
        assert book.id is not None

        chapters = session.exec(select(Chapter).where(Chapter.book_id == book.id)).all()
        assert chapters
        for chapter in chapters:
            assert chapter.body is not None


def test_create_or_update_book_allows_duplicate_content_different_paths(tmp_path: Path):
    books_dir = tmp_path / 'books'
    books_dir.mkdir(parents=True, exist_ok=True)
    source1 = books_dir / 'a.txt'
    source2 = books_dir / 'b.txt'
    content = '\n'.join(['第一章 开始', '正文1', '正文2', '正文3', '正文4', '正文5'])
    source1.write_text(content, encoding='utf-8')
    source2.write_text(content, encoding='utf-8')

    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        book1, is_new1 = create_or_update_book(
            session=session,
            file_path=source1,
            books_dir=books_dir,
            force_reparse=True,
        )
        book2, is_new2 = create_or_update_book(
            session=session,
            file_path=source2,
            books_dir=books_dir,
            force_reparse=True,
        )

        assert is_new1 is True
        assert is_new2 is True
        assert book1.id != book2.id
