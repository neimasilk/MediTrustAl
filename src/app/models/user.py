from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import enum
from pydantic import BaseModel, EmailStr, constr

from ..database import Base

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    blockchain_address = Column(String(42), unique=True)  # Ethereum address format
    did = Column(String(100), unique=True, nullable=False)  # Decentralized Identifier
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

# Pydantic models for request/response
class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    role: constr(pattern='^(PATIENT|DOCTOR|ADMIN)$')

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: str
    blockchain_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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