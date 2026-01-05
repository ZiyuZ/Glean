"""扫描服务：目录扫描和文件处理"""

import asyncio

from pydantic.main import BaseModel
from sqlmodel import Session, select
from sqlmodel.sql.expression import col

from ..core.config import settings
from ..core.models import Book
from .book_service import create_or_update_book


# 全局扫描状态
class ScanStatus(BaseModel):
    is_running: bool
    files_scanned: int
    files_added: int
    files_updated: int
    total_files: int
    current_file: str
    error: str | None


_scan_status = ScanStatus(
    is_running=False,
    files_scanned=0,
    files_added=0,
    files_updated=0,
    total_files=0,
    current_file='',
    error=None,
)


def get_scan_status() -> ScanStatus:
    """获取当前扫描状态"""
    return _scan_status


def reset_scan_status() -> None:
    """重置扫描状态"""
    _scan_status.is_running = False
    _scan_status.files_scanned = 0
    _scan_status.files_added = 0
    _scan_status.files_updated = 0
    _scan_status.total_files = 0
    _scan_status.current_file = ''
    _scan_status.error = None


async def scan_directory(session: Session, full_scan: bool = False) -> None:
    """
    扫描书籍目录

    参数:
        session: 数据库会话
        full_scan: 是否执行全量扫描（True）或增量扫描（False）
    """
    books_dir = settings.books_dir

    if not books_dir.exists():
        _scan_status.error = f'Books directory does not exist: {books_dir}'
        _scan_status.is_running = False
        return

    reset_scan_status()
    _scan_status.is_running = True

    try:
        # 收集所有 TXT 文件
        txt_files = list(books_dir.rglob('*.txt'))
        _scan_status.total_files = len(txt_files)

        # 获取数据库中所有书籍的 hash_id（用于检测已删除的文件）
        existing_books = session.exec(select(Book)).all()
        existing_hash_ids = {book.hash_id for book in existing_books}
        found_hash_ids = set[str]()

        # 处理每个文件
        for file_path in txt_files:
            if not _scan_status.is_running:
                break  # 允许取消扫描

            _scan_status.current_file = str(file_path.relative_to(books_dir))

            try:
                # 检查文件是否需要处理
                if not full_scan:
                    # 增量扫描：检查文件是否已存在且未修改
                    stat = file_path.stat()
                    existing_book = session.exec(
                        select(Book).where(Book.path == str(file_path.relative_to(books_dir)))
                    ).first()

                    if existing_book:
                        # 检查文件是否被修改
                        if (
                            existing_book.file_size == stat.st_size
                            and existing_book.file_mtime == stat.st_mtime
                        ):
                            # 文件未修改，跳过
                            found_hash_ids.add(existing_book.hash_id)
                            _scan_status.files_scanned += 1
                            continue

                # 处理文件（在后台线程中执行，因为涉及文件 I/O）
                # 全量扫描时强制重新解析
                loop = asyncio.get_event_loop()
                book, is_new = await loop.run_in_executor(
                    None,
                    create_or_update_book,
                    session,
                    file_path,
                    books_dir,
                    full_scan,  # 全量扫描时强制重新解析
                )

                found_hash_ids.add(book.hash_id)

                if is_new:
                    _scan_status.files_added += 1
                else:
                    _scan_status.files_updated += 1

                _scan_status.files_scanned += 1

            except Exception as e:
                # 记录错误但继续处理其他文件
                error_msg = f'Error processing {file_path}: {str(e)}'
                _scan_status.error = error_msg
                # 继续处理下一个文件
                continue

        # 删除数据库中不存在的文件记录
        deleted_hash_ids = existing_hash_ids - found_hash_ids
        if deleted_hash_ids:
            deleted_books = session.exec(
                select(Book).where(
                    col(Book.hash_id).in_(deleted_hash_ids),
                )
            ).all()
            for book in deleted_books:
                session.delete(book)
            session.commit()

    except Exception as e:
        _scan_status.error = f'Scan error: {str(e)}'
    finally:
        _scan_status.is_running = False
        _scan_status.current_file = ''


def stop_scan() -> None:
    """停止扫描"""
    _scan_status.is_running = False
