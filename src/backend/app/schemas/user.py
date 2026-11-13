
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    email: str
    phone: str
    full_name: str
    role: str
    avatar_url: str | None = None
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    avatar_url: str | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
