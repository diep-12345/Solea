
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_phone,
    update_user_profile,
    get_password_hash_by_user_id,
    update_user_password
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

password_hash = PasswordHash.recommended()


# 1. Xem thông tin cá nhân
@router.get("/me", response_model=UserResponse)
def get_my_information(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, current_user["user_id"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng"
        )

    return dict(user)


# 2. Cập nhật thông tin cá nhân
@router.put("/me", response_model=UserResponse)
def update_my_information(
    data: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]

    existing_phone = get_user_by_phone(db, data.phone)

    if existing_phone and existing_phone["user_id"] != user_id:
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại đã được sử dụng"
        )

    try:
        updated_user = update_user_profile(
            db,
            user_id,
            data.model_dump()
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Không thể cập nhật thông tin"
        )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng"
        )

    return dict(updated_user)


# 3. Đổi mật khẩu
@router.put("/change-password")
def change_password(
    data: PasswordChange,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]

    old_password_hash = get_password_hash_by_user_id(
        db, user_id
    )

    if not old_password_hash or not password_hash.verify(
        data.old_password,
        old_password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu hiện tại không chính xác"
        )

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu mới phải khác mật khẩu hiện tại"
        )

    new_password_hash = password_hash.hash(
        data.new_password
    )

    update_user_password(
        db,
        user_id,
        new_password_hash
    )

    return {
        "message": "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
    }
