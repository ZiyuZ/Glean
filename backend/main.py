from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.api import api_router
from src.core.config import settings
from src.core.database import init_db

# 确保必要的目录存在
settings.ensure_directories()

# 初始化数据库（创建表）
init_db()

# 判断是否为生产环境（通过检查是否存在前端构建目录）
FRONTEND_DIST = Path(__file__).parent.parent / 'frontend' / 'dist'
IS_PRODUCTION = FRONTEND_DIST.exists() and (FRONTEND_DIST / 'index.html').exists()

app = FastAPI(
    title='Glean (拾阅)',
    description='轻量级的、自托管的个人小说云阅工具',
    version='0.1.0',
)

# CORS 配置
if not IS_PRODUCTION:
    # 开发环境：允许前端开发服务器跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:5173'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# 注册 API 路由
app.include_router(api_router)

# 生产环境：挂载静态文件
if IS_PRODUCTION:
    # 挂载 Vite 构建的静态资源（assets）
    assets_dir = FRONTEND_DIST / 'assets'
    if assets_dir.exists():
        app.mount('/assets', StaticFiles(directory=str(assets_dir)), name='assets')

    # 根路由：返回前端入口文件
    @app.get('/')
    async def root():
        index_path = FRONTEND_DIST / 'index.html'
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail='Frontend not found')

    # Catch-all 路由：所有非 API 请求返回 index.html（支持 SPA 路由）
    @app.get('/{full_path:path}')
    async def serve_spa(request: Request, full_path: str):
        # 排除 API 路由和静态资源（这些路由已经在上面处理了）
        if full_path.startswith('api/') or full_path.startswith('assets/'):
            raise HTTPException(status_code=404)
        # 返回前端入口文件
        index_path = FRONTEND_DIST / 'index.html'
        if index_path.exists():
            return FileResponse(str(index_path))

        raise HTTPException(status_code=404, detail='Frontend not found')
else:
    # 开发环境：根路由返回 API 信息
    @app.get('/')
    async def root():
        return {'message': 'Glean API', 'version': '0.1.0'}


@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
