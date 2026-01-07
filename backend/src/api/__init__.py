from fastapi import APIRouter

from core.config import settings

from . import books, chapters, scan

api_router = APIRouter(prefix='/api')

# 注册所有路由
api_router.include_router(books.router, prefix='/books', tags=['books'])
api_router.include_router(chapters.router, prefix='/books', tags=['chapters'])
api_router.include_router(scan.router, prefix='/scan', tags=['scan'])


system_router = APIRouter()


@system_router.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok', 'version': settings.app_version}


@system_router.get('/version')
async def version() -> dict[str, str]:
    return {'app_version': settings.app_version, 'database_version': settings.database_version}


api_router.include_router(system_router, prefix='/system', tags=['system'])
