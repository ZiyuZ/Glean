from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings
from core.security import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    password: str


@router.post('/login')
async def login(data: LoginRequest) -> dict[str, str]:
    """
    登录接口。
    如果未启用验证，只需调用一次获取假 Token 即可。
    """
    if not settings.app_password:
        # 如果未设置密码，返回一个标记用的 Token
        return {'access_token': 'no-auth-needed', 'token_type': 'bearer'}

    if data.password != settings.app_password:
        raise HTTPException(status_code=401, detail='Passcode incorrect')

    # 生成长期有效的 Token
    access_token = create_access_token(data={'sub': 'admin'})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/auth-status')
async def auth_status() -> dict[str, bool]:
    """查询是否启用了身份验证"""
    return {'enabled': bool(settings.app_password)}


@router.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok', 'version': settings.app_version}


@router.get('/version')
async def version() -> dict[str, str]:
    return {'app_version': settings.app_version, 'database_version': settings.database_version}
