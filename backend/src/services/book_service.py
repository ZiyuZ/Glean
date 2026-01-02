"""书籍服务：创建和更新 Book 和 Chapter"""

from pathlib import Path

from sqlmodel import Session, select

from ..core.models import Book, Chapter
from .parser import calculate_file_hash, detect_encoding, parse_chapters


def create_or_update_book(
    session: Session,
    file_path: Path,
    books_dir: Path,
) -> tuple[Book, bool]:
    """
    创建或更新书籍

    参数:
        session: 数据库会话
        file_path: 文件路径（绝对路径）
        books_dir: 书籍目录（用于计算相对路径）

    返回:
        (book, is_new) - 书籍对象和是否为新创建的标志
    """
    # 获取文件元数据
    stat = file_path.stat()
    file_size = stat.st_size
    file_mtime = stat.st_mtime

    # 检测编码
    encoding = detect_encoding(file_path)

    # 计算文件哈希
    hash_id = calculate_file_hash(file_path)

    # 计算相对路径（用于存储）
    try:
        relative_path = file_path.relative_to(books_dir)
    except ValueError:
        # 如果文件不在 books_dir 内，使用绝对路径
        relative_path = Path(file_path)

    # 检查书籍是否已存在
    existing_book = session.exec(select(Book).where(Book.hash_id == hash_id)).first()

    if existing_book:
        # 更新现有书籍
        is_new = False
        book = existing_book

        # 检查文件是否被修改（通过 file_size 和 file_mtime）
        if book.file_size != file_size or book.file_mtime != file_mtime:
            # 文件被修改，需要重新解析
            book.file_size = file_size
            book.file_mtime = file_mtime
            book.encoding = encoding
            book.path = str(relative_path)

            # 删除旧章节
            old_chapters = session.exec(select(Chapter).where(Chapter.book_id == book.id)).all()
            for chapter in old_chapters:
                session.delete(chapter)

            # 解析新章节
            chapters_data = parse_chapters(file_path, encoding)
            for chapter_data in chapters_data:
                chapter = Chapter(
                    book_id=book.id,
                    title=chapter_data['title'],
                    order_index=chapter_data['order_index'],
                    start_byte=chapter_data['start_byte'],
                    end_byte=chapter_data['end_byte'],
                )
                session.add(chapter)

            session.add(book)
            session.commit()
            session.refresh(book)
    else:
        # 创建新书籍
        is_new = True

        # 解析章节
        chapters_data = parse_chapters(file_path, encoding)

        # 提取书名（使用文件名，去掉扩展名）
        title = file_path.stem

        # 创建书籍
        book = Book(
            hash_id=hash_id,
            title=title,
            path=str(relative_path),
            file_size=file_size,
            file_mtime=file_mtime,
            encoding=encoding,
        )
        session.add(book)
        session.flush()  # 获取 book.id

        # 创建章节
        for chapter_data in chapters_data:
            chapter = Chapter(
                book_id=book.id,
                title=chapter_data['title'],
                order_index=chapter_data['order_index'],
                start_byte=chapter_data['start_byte'],
                end_byte=chapter_data['end_byte'],
            )
            session.add(chapter)

        session.commit()
        session.refresh(book)

    return book, is_new


def reparse_book(session: Session, book_id: int, books_dir: Path) -> Book:
    """
    重新解析指定书籍

    用于手动触发重新解析
    """
    book = session.get(Book, book_id)
    if not book:
        raise ValueError(f'Book with id {book_id} not found')

    # 构建完整文件路径
    file_path = books_dir / book.path
    if not file_path.exists():
        raise ValueError(f'Book file not found: {file_path}')

    # 删除旧章节
    old_chapters = session.exec(select(Chapter).where(Chapter.book_id == book.id)).all()
    for chapter in old_chapters:
        session.delete(chapter)

    # 重新解析
    book, _ = create_or_update_book(session, file_path, books_dir)

    return book
