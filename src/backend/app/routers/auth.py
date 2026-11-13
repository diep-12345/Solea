
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import bearer_scheme, get_current_user
from app.database import get_db
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)
from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_phone,
    create_user
)
from app.repositories.token_repository import revoke_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)


# 1. Đăng ký tài khoản
@router.post("/register", response_model=UserResponse)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=400,
            detail="Email đã được sử dụng"
        )

    if get_user_by_phone(db, data.phone):
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại đã được sử dụng"
        )

    hashed_password = password_hash.hash(data.password)

    try:
        new_user = create_user(
            db=db,
            email=data.email,
            phone=data.phone,
            password_hash=hashed_password,
            full_name=data.full_name
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email hoặc số điện thoại đã tồn tại"
        )

    return dict(new_user)


# 2. Đăng nhập
@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, data.email)

    if not user or not password_hash.verify(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không chính xác"
        )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=EXPIRE_MINUTES
    )

    token = jwt.encode(
        {
            "sub": str(user["user_id"]),
            "role": user["role"],
            "token_version": user["token_version"],
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


# 3. Đăng xuất
@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "token_version"]}
        )

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )

    revoke_token(
        db,
        token,
        expires_at
    )

    return {
        "message": "Đăng xuất thành công"
    }
