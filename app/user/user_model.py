# app/user/user_model.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
from app.common.base_model import BaseDBModel

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseDBModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    full_name: str

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError('Username must be alphanumeric')
        return v