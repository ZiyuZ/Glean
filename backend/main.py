from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import api_router

app = FastAPI(
    title='Glean (拾阅)',
    description='轻量级的、自托管的个人小说云阅工具',
    version='0.1.0',
)

# CORS 配置（开发环境允许所有来源，生产环境需要限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # TODO: 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 注册 API 路由
app.include_router(api_router)


@app.get('/')
async def root():
    return {'message': 'Glean API', 'version': '0.1.0'}


@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
