from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from core.config import settings

ALGORITHM = 'HS256'


def create_access_token(data: dict[str, Any]) -> str:
    """创建永不过期的访问令牌 (实际有效期 100 年)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=36500)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
