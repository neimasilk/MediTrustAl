import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, String, Enum as SQLEnum, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from src.app.core.database import Base


class RecordType(PyEnum):
    DIAGNOSIS = "DIAGNOSIS"
    LAB_RESULT = "LAB_RESULT"
    PRESCRIPTION = "PRESCRIPTION"
    TREATMENT_PLAN = "TREATMENT_PLAN"
    MEDICAL_HISTORY = "MEDICAL_HISTORY"
    VITAL_SIGNS = "VITAL_SIGNS"
    IMAGING = "IMAGING"
    VACCINATION = "VACCINATION"


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Changed server_default to default
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    blockchain_record_id = Column(String(66), unique=True, nullable=True)
    record_type = Column(SQLEnum(RecordType, name="recordtype"), nullable=False)
    record_metadata = Column(JSONB, nullable=True) # Renamed from metadata
    encrypted_data = Column(LargeBinary, nullable=False)
    data_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User", back_populates="medical_records")


class MedicalRecordBase(BaseModel):
    record_type: RecordType
    record_metadata: Optional[dict] = None # Renamed from metadata
    raw_data: str


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    record_type: RecordType
    record_metadata: Optional[dict] = None
    blockchain_record_id: Optional[str] = None
    data_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordDetailResponse(MedicalRecordResponse):
    raw_data: Optional[str] = None
