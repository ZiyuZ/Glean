import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select
from sqlmodel.sql.expression import col

from core.config import settings
from core.database import get_db_session
from core.models import Book, Chapter
from core.schemas import MarkFinishedRequest, MessageResponse, ToggleStarRequest, UpdateProgressRequest
from services.book_service import reparse_book as reparse_book_service

router = APIRouter()


def check_book_finished(book: Book, chapters: list[Chapter]) -> bool:
    """
    检查并更新书籍的完成状态

    判断逻辑：
    1. 必须有阅读进度（chapter_index 不为 None）
    2. 当前章节必须是最后一章
    3. 当前章节的偏移量接近章节末尾（剩余 < 5% 或 < 200字符，取较大值）

    返回：是否已读完
    """
    if book.chapter_index is None or not chapters:
        book.is_finished = False
        return False

    # 找到最后一章
    last_chapter = max(chapters, key=lambda c: c.order_index)
    last_chapter_index = last_chapter.order_index

    # 如果当前章节不是最后一章，肯定没读完
    if book.chapter_index < last_chapter_index:
        book.is_finished = False
        return False

    # 如果当前章节是最后一章，检查偏移量
    if book.chapter_index == last_chapter_index:
        chapter_size = len(last_chapter.content)  # 使用字符长度
        if book.chapter_offset is not None and chapter_size > 0:
            remaining = chapter_size - book.chapter_offset
            # 判断标准：剩余 < 5% 或 < 200字符（取较大值，适应不同屏幕）
            threshold = max(chapter_size * 0.05, 200)
            is_finished = remaining <= threshold
            book.is_finished = is_finished
            return is_finished

    book.is_finished = False
    return False


@router.get('')
async def list_books(
    starred: bool | None = Query(None, description='筛选标星书籍'),
    search: str | None = Query(None, description='搜索书名'),
    finished: bool | None = Query(None, description='筛选已读完/未读完的书籍'),
    started: bool | None = Query(None, description='筛选是否已开始阅读'),
    session: Session = Depends(get_db_session),
) -> list[Book]:
    """
    获取书架列表

    - 支持按标星状态筛选
    - 支持按书名搜索
    - 支持按是否读完筛选
    - 支持按是否开始阅读筛选
    - 返回书籍列表（前端可根据 chapter_index、chapter_offset、chapters 计算进度）
    """
    statement = select(Book)
    if starred is not None:
        statement = statement.where(Book.is_starred == starred)
    if search:
        statement = statement.where(col(Book.title).contains(search))
    if finished is not None:
        statement = statement.where(Book.is_finished == finished)
    if started is not None:
        if started:
            statement = statement.where(Book.chapter_index != None)  # noqa: E711
        else:
            statement = statement.where(Book.chapter_index == None)  # noqa: E711
    books = session.exec(statement).all()
    return list(books)


@router.get('/random')
async def get_random_books(
    count: int = Query(1, ge=1, le=100, description='返回的随机书籍数量'),
    session: Session = Depends(get_db_session),
) -> list[Book]:
    """
    随机获取指定数量的书籍（发现功能）

    - count: 返回的书籍数量（1-100，默认 1）
    """
    statement = select(Book).order_by(func.random()).limit(count)
    books = session.exec(statement).all()
    if not books:
        raise HTTPException(status_code=404, detail='No books found')
    return list(books)


@router.get('/{book_id}')
async def get_book(
    book_id: int,
    session: Session = Depends(get_db_session),
) -> Book:
    """
    获取书籍详情
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')
    return book


@router.patch('/{book_id}/progress')
async def update_progress(
    book_id: int,
    request: UpdateProgressRequest,
    session: Session = Depends(get_db_session),
) -> Book:
    """
    同步阅读进度

    - chapter_index: 当前阅读的章节索引
    - chapter_offset: 在章节内的字符偏移量

    注意：会自动判断并更新 is_finished 状态
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    book.chapter_index = request.chapter_index
    book.chapter_offset = request.chapter_offset
    book.last_read_time = time.time()

    # 加载章节数据并检查完成状态
    chapters_stmt = select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.order_index)
    chapters = list(session.exec(chapters_stmt).all())
    book.is_finished = check_book_finished(book, chapters)

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@router.patch('/{book_id}/finish')
async def mark_finished(
    book_id: int,
    request: MarkFinishedRequest,
    session: Session = Depends(get_db_session),
) -> Book:
    """
    手动标记书籍为已读完/未读完

    - finished: true 表示标记为已读完，false 表示标记为未读完
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    book.is_finished = request.finished
    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@router.patch('/{book_id}/star')
async def toggle_star(
    book_id: int,
    request: ToggleStarRequest,
    session: Session = Depends(get_db_session),
) -> Book:
    """
    标星/取消标星
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')
    book.is_starred = request.starred
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.post('/{book_id}/reparse')
async def reparse_book_endpoint(
    book_id: int,
    session: Session = Depends(get_db_session),
) -> Book:
    """
    重新解析指定书籍

    用于手动触发重新解析，适用于：
    - 文件内容被修改
    - 章节解析规则更新
    - 编码检测失败需要重新检测
    """
    try:
        book = reparse_book_service(session, book_id, settings.books_dir)
        return book
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{book_id}')
async def delete_book(
    book_id: int,
    physical: bool = Query(True, description='是否物理删除文件'),
    session: Session = Depends(get_db_session),
) -> MessageResponse:
    """
    删除书籍

    - physical=True: 同时删除数据库记录和物理文件
    - physical=False: 仅删除数据库记录（从书架移除）
    删除书籍或从书架移除

    - physical=True: 物理删除书籍文件和所有数据库记录（书籍及章节）。
    - physical=False: 逻辑删除，仅重置书籍的阅读进度（chapter_index, chapter_offset,
      is_finished, last_read_time），使其从“已开始阅读”状态中移除，但保留书籍记录和文件。
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail='书籍未找到')

    if not physical:
        # 逻辑删除：仅重置阅读进度（移出书架）
        book.chapter_index = None
        book.chapter_offset = None
        book.is_finished = False
        book.last_read_time = None
        session.add(book)
        session.commit()
        session.refresh(book)
        return MessageResponse(message='已移出书架')

    # 物理删除：删除文件 + 数据库记录
    # 1. 删除物理文件
    file_path = Path(book.path)
    # 如果是相对路径，尝试拼接
    if not file_path.is_absolute():
        file_path = settings.books_dir / file_path

    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            # 文件删除失败（如被占用），但仍继续删除数据库记录？
            print(f'Error deleting file {file_path}: {e}')

    # 2. 删除关联章节 (避免 IntegrityError)
    chapters = session.exec(select(Chapter).where(Chapter.book_id == book.id)).all()
    for chapter in chapters:
        session.delete(chapter)

    # 3. 删除书籍记录
    session.delete(book)
    session.commit()
    return MessageResponse(message='书籍已彻底删除')
