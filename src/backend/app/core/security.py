
import os

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import get_user_by_id
from app.repositories.token_repository import is_token_revoked


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=False)


# Xác thực người dùng đang đăng nhập
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="Chưa cấu hình SECRET_KEY"
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "token_version"]}
        )

        user_id = payload.get("sub")
        token_version = payload.get("token_version")

        if not user_id or not str(user_id).isdigit():
            raise HTTPException(
                status_code=401,
                detail="Token không hợp lệ"
            )

        if not isinstance(token_version, int):
            raise HTTPException(
                status_code=401,
                detail="Token không hợp lệ"
            )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if is_token_revoked(db, token):
        raise HTTPException(
            status_code=401,
            detail="Token đã bị thu hồi"
        )

    user = get_user_by_id(db, int(user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Người dùng không tồn tại"
        )

    if token_version != user["token_version"]:
        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại"
        )

    return user


# Kiểm tra quyền Admin
def require_admin(
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập chức năng này"
        )

    return current_user
