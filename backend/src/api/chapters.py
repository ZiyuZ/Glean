from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select

from ..core.database import get_db_session
from ..core.models import Book, Chapter

router = APIRouter()


@router.get('/books/{book_id}/chapters')
async def list_chapters(
    book_id: int,
    session: Session = Depends(get_db_session),
) -> list[Chapter]:
    """
    获取书籍的章节目录

    返回章节列表，包含标题和索引信息
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    statement = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order_index)
    chapters = session.exec(statement).all()
    return list(chapters)


@router.get('/books/{book_id}/content/{chapter_index}')
async def get_chapter_content(
    book_id: int,
    chapter_index: int,
    session: Session = Depends(get_db_session),
) -> PlainTextResponse:
    """
    获取特定章节的纯文本内容

    根据章节索引和字节偏移量，直接从文件中读取对应章节内容
    返回纯文本格式，前端负责渲染
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    # 查找章节
    statement = select(Chapter).where(
        Chapter.book_id == book_id,
        Chapter.order_index == chapter_index,
    )
    chapter = session.exec(statement).first()
    if not chapter:
        raise HTTPException(status_code=404, detail='Chapter not found')

    # 使用字节偏移量读取章节内容
    file_path = Path(book.path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail='Book file not found')

    with open(file_path, 'rb') as f:
        f.seek(chapter.start_byte)
        content_bytes = f.read(chapter.end_byte - chapter.start_byte)

    # 根据缓存的编码解码（encoding 在扫描时已确定，不会是 None）
    try:
        content = content_bytes.decode(book.encoding)
    except UnicodeDecodeError:
        # 如果解码失败，返回报错信息
        raise HTTPException(status_code=500, detail='Failed to decode content')

    return PlainTextResponse(content)
