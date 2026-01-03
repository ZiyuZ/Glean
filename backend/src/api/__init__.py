from fastapi import APIRouter

from . import books, chapters, scan

api_router = APIRouter(prefix='/api')

# 注册所有路由
api_router.include_router(books.router, prefix='/books', tags=['books'])
api_router.include_router(chapters.router, prefix='/books', tags=['chapters'])
api_router.include_router(scan.router, prefix='/scan', tags=['scan'])
