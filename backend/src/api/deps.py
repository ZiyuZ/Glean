from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.security import verify_token

# 定义 OAuth2 方案，用于 Swagger UI 和 Token 提取
# auto_error=False 允许我们在依赖中手动处理逻辑（比如未配置密码时跳过）
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl='/api/system/login', auto_error=False)


async def check_auth(token: Annotated[str | None, Depends(reusable_oauth2)]) -> bool:
    """
    验证身份。

    逻辑：
    1. 如果未配置 APP_PASSWORD，视为无锁模式，直接通过。
    2. 如果配置了密码，检查 Token 是否存在且有效。
    """
    # 如果未设置密码，直接放行
    if not settings.app_password:
        return True

    # 检查是否有 Token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # 验证 Token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return True
