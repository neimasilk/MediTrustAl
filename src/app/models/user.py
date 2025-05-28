from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..core.database import Base
from ..schemas.user import UserRole

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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship to MedicalRecord
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"