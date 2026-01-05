from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.api import api_router
from src.core.config import settings
from src.core.database import init_db
from src.core.log import setup_logging

__version__ = '0.2.0'

# 设置日志
setup_logging()

# 确保必要的目录存在
settings.ensure_directories()

# 初始化数据库（创建表）
init_db()

IS_PRODUCTION = settings.is_production

app = FastAPI(
    title='Glean (拾阅)',
    description='轻量级的、自托管的个人小说云阅工具',
    version=__version__,
)

# CORS 配置
if not IS_PRODUCTION:
    # 开发环境：允许前端开发服务器跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# 注册 API 路由
app.include_router(api_router)

# 生产环境：挂载静态文件（如果存在）
if IS_PRODUCTION:
    FRONTEND_DIST = Path('/app/frontend/dist')
    FRONTEND_INDEX = FRONTEND_DIST / 'index.html'
    app.mount('/assets', StaticFiles(directory=str(FRONTEND_DIST / 'assets')), name='assets')

    # 根路由：返回前端入口文件
    @app.get('/')
    async def root_prod():
        return FileResponse(str(FRONTEND_INDEX))

    # Catch-all 路由：所有非 API 请求返回 index.html（支持 SPA 路由）
    # Catch-all 路由：所有非 API 请求返回 index.html（支持 SPA 路由）
    @app.get('/{full_path:path}')
    async def serve_spa(_request: Request, full_path: str):
        # 排除 API 请求
        if full_path.startswith('api/'):
            raise HTTPException(status_code=404)

        # 检查是否请求根目录下的静态文件 (如 manifest.webmanifest, favicon.ico, sw.js 等)
        # 注意: /assets 已经被上面的 app.mount 处理了
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # SPA 路由 fallback -> index.html
        if FRONTEND_INDEX.exists():
            return FileResponse(str(FRONTEND_INDEX))

        raise HTTPException(status_code=404, detail='Frontend not found')
else:
    # 开发环境：根路由返回 API 信息
    @app.get('/')
    async def root_dev():
        return {'message': 'Glean API', 'version': __version__}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
