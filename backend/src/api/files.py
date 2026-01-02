from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class FileItem(BaseModel):
    name: str
    path: str
    is_file: bool
    size: int | None = None  # 仅文件有大小


class FileListResponse(BaseModel):
    folders: list[FileItem]
    files: list[FileItem]
    current_path: str


@router.get('')
async def list_files(
    path: str = Query('', description='相对路径，默认为根目录'),
    # TODO: 需要配置的数据目录路径
) -> FileListResponse:
    """
    浏览文件系统目录

    返回指定路径下的文件夹和文件列表
    用于前端的文件浏览功能

    注意：需要严格校验路径，防止路径遍历攻击
    """
    # TODO: 实现文件浏览逻辑
    # # 获取配置的数据目录
    # data_dir = Path(config.DATA_DIR)
    #
    # # 规范化并校验路径，防止路径遍历
    # requested_path = Path(path)
    # if requested_path.is_absolute() or '..' in str(requested_path):
    #     raise HTTPException(status_code=400, detail='Invalid path')
    #
    # full_path = (data_dir / requested_path).resolve()
    #
    # # 确保路径在数据目录内
    # if not str(full_path).startswith(str(data_dir.resolve())):
    #     raise HTTPException(status_code=403, detail='Path traversal detected')
    #
    # if not full_path.exists():
    #     raise HTTPException(status_code=404, detail='Path not found')
    #
    # if not full_path.is_dir():
    #     raise HTTPException(status_code=400, detail='Path is not a directory')
    #
    # folders = []
    # files = []
    #
    # for item in full_path.iterdir():
    #     if item.is_dir():
    #         folders.append(FileItem(
    #             name=item.name,
    #             path=str(item.relative_to(data_dir)),
    #             is_file=False
    #         ))
    #     elif item.suffix.lower() == '.txt':
    #         files.append(FileItem(
    #             name=item.name,
    #             path=str(item.relative_to(data_dir)),
    #             is_file=True,
    #             size=item.stat().st_size
    #         ))
    #
    # # 排序：文件夹在前，按名称排序
    # folders.sort(key=lambda x: x.name)
    # files.sort(key=lambda x: x.name)
    #
    # return FileListResponse(
    #     folders=folders,
    #     files=files,
    #     current_path=str(requested_path)
    # )
    raise HTTPException(status_code=501, detail='Not implemented yet')
