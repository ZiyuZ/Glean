from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select

from ..core.database import get_db_session
from ..core.models import Book, Chapter
from ..core.schemas import ChapterMetadata

router = APIRouter()


@router.get('/{book_id}/chapters', response_model=list[ChapterMetadata])
async def list_chapters(
    book_id: int,
    session: Session = Depends(get_db_session),
) -> list[ChapterMetadata]:
    """
    获取书籍的章节目录


    返回章节列表，包含标题和索引信息
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    statement = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order_index)
    chapters = session.exec(statement).all()
    return [
        ChapterMetadata(
            id=c.id,
            book_id=c.book_id,
            title=c.title,
            order_index=c.order_index,
        )
        for c in chapters
    ]


@router.get('/{book_id}/chapters/{chapter_index}')
async def get_chapter_content(
    book_id: int,
    chapter_index: int,
    session: Session = Depends(get_db_session),
) -> PlainTextResponse:
    """
    获取特定章节的纯文本内容

    直接从数据库读取章节内容
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
        raise HTTPException(
            status_code=404, detail=f'Chapter not found: book_id={book_id}, chapter_index={chapter_index}'
        )

    # 直接从数据库读取内容
    return PlainTextResponse(chapter.content)
