
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_phone,
    update_user_profile
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


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

    # Kiểm tra số điện thoại đã được sử dụng chưa
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
