from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..core.database import get_db_session

router = APIRouter()


class ScanResponse(BaseModel):
    message: str
    files_scanned: int = 0
    files_added: int = 0
    files_updated: int = 0


@router.post('')
async def trigger_scan(
    background_tasks: BackgroundTasks,
    full_scan: bool = False,
    session: Session = Depends(get_db_session),
) -> ScanResponse:
    """
    手动触发目录扫描

    - full_scan: 是否执行全量扫描（默认增量扫描）

    扫描逻辑：
    1. 遍历指定目录下的所有 TXT 文件
    2. 对于新文件：计算 hash_id，解析章节，插入数据库
    3. 对于已存在文件：检查 file_size 和 file_mtime，如果变更则重新解析
    4. 对于已删除文件：从数据库中移除
    """
    # TODO: 实现扫描逻辑
    # async def scan_task():
    #     # 扫描逻辑
    #     pass
    #
    # if full_scan:
    #     background_tasks.add_task(scan_task, full=True)
    # else:
    #     background_tasks.add_task(scan_task, full=False)
    #
    # return ScanResponse(
    #     message='Scan started',
    #     files_scanned=0,
    #     files_added=0,
    #     files_updated=0
    # )
    raise HTTPException(status_code=501, detail='Not implemented yet')
