from fastapi import APIRouter, Depends

from api.deps import check_auth

from . import books, chapters, scan, system

api_router = APIRouter(prefix='/api')

# Public Routes (System: Login, Health, etc.)
api_router.include_router(system.router, prefix='/system', tags=['system'])

# Protected Routes
api_router.include_router(books.router, prefix='/books', tags=['books'], dependencies=[Depends(check_auth)])
api_router.include_router(
    chapters.router, prefix='/books', tags=['chapters'], dependencies=[Depends(check_auth)]
)
api_router.include_router(scan.router, prefix='/scan', tags=['scan'], dependencies=[Depends(check_auth)])
