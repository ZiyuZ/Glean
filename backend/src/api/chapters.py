from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ..core.models import Chapter

router = APIRouter()


@router.get('/books/{book_id}/chapters')
async def list_chapters(
    book_id: int,
    # TODO: 需要数据库会话依赖
) -> list[Chapter]:
    """
    获取书籍的章节目录

    返回章节列表，包含标题和索引信息
    """
    # TODO: 实现查询逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    #
    # statement = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order_index)
    # chapters = session.exec(statement).all()
    # return chapters
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.get('/books/{book_id}/content/{chapter_index}')
async def get_chapter_content(
    book_id: int,
    chapter_index: int,
    # TODO: 需要数据库会话依赖
) -> PlainTextResponse:
    """
    获取特定章节的纯文本内容

    根据章节索引和字节偏移量，直接从文件中读取对应章节内容
    返回纯文本格式，前端负责渲染
    """
    # TODO: 实现章节内容读取逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    #
    # # 查找章节
    # statement = select(Chapter).where(
    #     Chapter.book_id == book_id,
    #     Chapter.order_index == chapter_index
    # )
    # chapter = session.exec(statement).first()
    # if not chapter:
    #     raise HTTPException(status_code=404, detail='Chapter not found')
    #
    # # 使用字节偏移量读取章节内容
    # file_path = Path(book.path)
    # with open(file_path, 'rb') as f:
    #     f.seek(chapter.start_byte)
    #     content_bytes = f.read(chapter.end_byte - chapter.start_byte)
    #
    # # 根据缓存的编码解码
    # encoding = book.encoding or 'utf-8'
    # content = content_bytes.decode(encoding)
    #
    # return PlainTextResponse(content)
    raise HTTPException(status_code=501, detail='Not implemented yet')
