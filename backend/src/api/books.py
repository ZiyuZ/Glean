from fastapi import APIRouter, HTTPException, Query

from ..core.models import Book

router = APIRouter()


@router.get('')
async def list_books(
    starred: bool | None = Query(None, description='筛选标星书籍'),
    search: str | None = Query(None, description='搜索书名'),
    # TODO: 需要数据库会话依赖
) -> list[Book]:
    """
    获取书架列表

    - 支持按标星状态筛选
    - 支持按书名搜索
    - 返回书籍列表，包含阅读进度信息
    """
    # TODO: 实现数据库查询逻辑
    # session: Session = Depends(get_session)
    # statement = select(Book)
    # if starred is not None:
    #     statement = statement.where(Book.is_starred == starred)
    # if search:
    #     statement = statement.where(Book.title.contains(search))
    # books = session.exec(statement).all()
    # return books
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.get('/random')
async def get_random_book(
    # TODO: 需要数据库会话依赖
) -> Book:
    """
    随机获取一本书籍（发现功能）
    """
    # TODO: 实现随机选择逻辑
    # session: Session = Depends(get_session)
    # statement = select(Book).order_by(func.random())
    # book = session.exec(statement).first()
    # if not book:
    #     raise HTTPException(status_code=404, detail='No books found')
    # return book
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.get('/{book_id}')
async def get_book(
    book_id: int,
    # TODO: 需要数据库会话依赖
) -> Book:
    """
    获取书籍详情
    """
    # TODO: 实现查询逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    # return book
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.patch('/{book_id}/progress')
async def update_progress(
    book_id: int,
    chapter_index: int,
    chapter_offset: int,
    # TODO: 需要数据库会话依赖和请求体模型
) -> Book:
    """
    同步阅读进度

    - chapter_index: 当前阅读的章节索引
    - chapter_offset: 在章节内的字节偏移量
    """
    # TODO: 实现进度更新逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    # book.chapter_index = chapter_index
    # book.chapter_offset = chapter_offset
    # book.last_read_time = time.time()
    # session.add(book)
    # session.commit()
    # session.refresh(book)
    # return book
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.patch('/{book_id}/star')
async def toggle_star(
    book_id: int,
    starred: bool,
    # TODO: 需要数据库会话依赖
) -> Book:
    """
    标星/取消标星
    """
    # TODO: 实现标星逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    # book.is_starred = starred
    # session.add(book)
    # session.commit()
    # session.refresh(book)
    # return book
    raise HTTPException(status_code=501, detail='Not implemented yet')


@router.delete('/{book_id}')
async def delete_book(
    book_id: int,
    # TODO: 需要数据库会话依赖
) -> dict:
    """
    从物理磁盘删除文件

    注意：此操作会同时删除数据库记录和物理文件
    """
    # TODO: 实现删除逻辑
    # session: Session = Depends(get_session)
    # book = session.get(Book, book_id)
    # if not book:
    #     raise HTTPException(status_code=404, detail='Book not found')
    #
    # # 删除物理文件
    # file_path = Path(book.path)
    # if file_path.exists():
    #     file_path.unlink()
    #
    # # 删除数据库记录（级联删除章节）
    # session.delete(book)
    # session.commit()
    # return {'message': 'Book deleted successfully'}
    raise HTTPException(status_code=501, detail='Not implemented yet')
