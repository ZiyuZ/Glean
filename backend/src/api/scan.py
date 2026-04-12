from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from sqlmodel import delete

from core.database import get_session
from core.models import Book, Chapter
from core.schemas import MessageResponse, ScanResponse
from services.scanner import (
    ScanStatus,
    begin_clear_database,
    end_clear_database,
    get_scan_status,
    scan_directory,
    stop_scan,
)

router = APIRouter()


async def scan_task(full_scan: bool) -> None:
    """后台扫描任务"""
    try:
        with get_session() as session:
            await scan_directory(session, full_scan=full_scan)
    except Exception as e:
        logger.exception('Unhandled exception in background scan task: ', e)


def clear_database_job() -> None:
    """后台线程中执行清空（避免长时间阻塞 HTTP 请求）"""
    try:
        with get_session() as session:
            session.exec(delete(Chapter))
            session.exec(delete(Book))
    except Exception as e:
        logger.exception('Clear database failed')
        end_clear_database(error=str(e))
    else:
        end_clear_database()


@router.post('')
async def trigger_scan(
    background_tasks: BackgroundTasks,
    full_scan: bool = False,
) -> ScanResponse:
    """
    手动触发目录扫描

    - full_scan: 是否执行全量扫描（默认增量扫描）

    扫描逻辑：
    1. 遍历指定目录下的所有 TXT 文件
    2. 对于新文件：计算 hash_id，解析章节，插入数据库
    3. 对于已存在文件：检查 file_size 和 file_mtime，如果变更则重新解析
    4. 对于已删除文件：从数据库中移除

    注意：扫描在后台异步执行，可通过 GET /api/scan/status 查询进度
    """
    status = get_scan_status()
    if status.is_clearing:
        raise HTTPException(status_code=409, detail='正在清空数据库，请稍候再扫描')
    if status.is_running:
        raise HTTPException(status_code=409, detail='扫描任务已在运行中')
    logger.info('Starting scan...')
    # 启动后台任务
    background_tasks.add_task(scan_task, full_scan)

    return ScanResponse(
        message='扫描任务已启动',
        files_scanned=0,
        files_added=0,
        files_updated=0,
    )


@router.get('/status')
async def get_status() -> ScanStatus:
    """
    获取扫描状态

    前端可以轮询此接口来获取扫描进度
    """
    return get_scan_status()


@router.post('/stop')
async def stop_scanning() -> MessageResponse:
    """
    停止正在进行的扫描
    """
    stop_scan()
    return MessageResponse(message='已请求停止扫描')


@router.post('/clear')
async def clear_database(background_tasks: BackgroundTasks) -> MessageResponse:
    """
    清空数据库（后台执行，立即返回；通过 GET /api/scan/status 的 is_clearing 轮询进度）

    警告：这将删除所有书籍、章节和阅读进度！
    """
    status = get_scan_status()
    if status.is_running:
        raise HTTPException(status_code=409, detail='扫描正在运行中，无法清空数据库')
    if status.is_clearing:
        raise HTTPException(status_code=409, detail='清空任务正在进行中')

    logger.warning('Scheduling database clear in background...')
    begin_clear_database()
    background_tasks.add_task(clear_database_job)

    return MessageResponse(message='清空任务已启动，正在后台执行')
