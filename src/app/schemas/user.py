from typing import Optional
from pydantic import BaseModel, EmailStr, constr, ConfigDict
import uuid
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

# Pydantic models for request/response
class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    full_name: constr(min_length=1, max_length=100)
    role: constr(pattern='^(PATIENT|DOCTOR|ADMIN)$')

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    role: Optional[constr(pattern='^(PATIENT|DOCTOR|ADMIN)$')] = None

class UserResponse(UserBase):
    id: uuid.UUID
    did: str
    blockchain_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserResponse):
    hashed_password: str

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: str | None = None
    role: str | None = None

class UserLogin(BaseModel):
    username_or_email: str
    password: constr(min_length=8)