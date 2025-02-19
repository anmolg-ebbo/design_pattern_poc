# app/user/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from app.user.user_model import UserStatus

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None