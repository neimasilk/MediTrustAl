from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship # Added import
import enum
import uuid # Added import for uuid.UUID
from pydantic import BaseModel, EmailStr, constr

from ..core.database import Base

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True) # Added full_name column
    hashed_password = Column(String(255), nullable=False)
    blockchain_address = Column(String(42), unique=True, nullable=True)  # Ethereum address format, can be nullable
    did = Column(String(100), unique=True, nullable=False)  # Decentralized Identifier
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to MedicalRecord
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

# Pydantic models for request/response
class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    full_name: constr(min_length=1, max_length=100) # Added full_name
    role: constr(pattern='^(PATIENT|DOCTOR|ADMIN)$')

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: uuid.UUID # Changed from str to uuid.UUID
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