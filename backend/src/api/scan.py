from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlmodel import delete

from ..core.database import get_session
from ..core.models import Book, Chapter
from ..services.scanner import get_scan_status, scan_directory, stop_scan

router = APIRouter()


class ScanResponse(BaseModel):
    message: str
    files_scanned: int = 0
    files_added: int = 0
    files_updated: int = 0


class ScanStatusResponse(BaseModel):
    is_running: bool
    files_scanned: int
    files_added: int
    files_updated: int
    total_files: int
    current_file: str
    error: str | None = None


async def scan_task(full_scan: bool) -> None:
    """后台扫描任务"""
    with get_session() as session:
        await scan_directory(session, full_scan=full_scan)


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
    if status['is_running']:
        raise HTTPException(status_code=409, detail='Scan is already running')

    # 启动后台任务
    background_tasks.add_task(scan_task, full_scan)

    return ScanResponse(
        message='Scan started',
        files_scanned=0,
        files_added=0,
        files_updated=0,
    )


@router.get('/status')
async def get_status() -> ScanStatusResponse:
    """
    获取扫描状态

    前端可以轮询此接口来获取扫描进度
    """
    status = get_scan_status()
    return ScanStatusResponse(**status)


@router.post('/stop')
async def stop_scanning() -> dict[str, str]:
    """
    停止正在进行的扫描
    """
    stop_scan()
    return {'message': 'Scan stop requested'}


@router.post('/clear')
async def clear_database() -> dict[str, str]:
    """
    清空数据库

    警告：这将删除所有书籍、章节和阅读进度！
    """
    status = get_scan_status()
    if status['is_running']:
        raise HTTPException(status_code=409, detail='Scan is running')

    with get_session() as session:
        session.exec(delete(Chapter))
        session.exec(delete(Book))
        session.commit()

    return {'message': 'Database cleared successfully'}
