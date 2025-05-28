import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator
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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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

    model_config = ConfigDict(from_attributes=True)


class MedicalRecordDetailResponse(MedicalRecordResponse):
    raw_data: Optional[str] = None


from pydantic import BaseModel, ConfigDict, field_validator # Added field_validator

# ... (rest of the existing imports) ...

# (Existing code for RecordType, MedicalRecord, MedicalRecordBase, MedicalRecordCreate, MedicalRecordResponse, MedicalRecordDetailResponse)
# ... (ensure these are kept as they are) ...


# Pydantic models for new Access Control Endpoints

class GrantAccessRequest(BaseModel):
    doctor_address: str

    @field_validator('doctor_address')
    @classmethod
    def validate_doctor_address(cls, v: str) -> str:
        # Basic validation for Ethereum address format (0x followed by 40 hex chars)
        # More robust validation can be done using Web3.is_address if web3 is easily available here
        # or by relying on the BlockchainService/endpoint to do the full check.
        if not isinstance(v, str) or not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum address format')
        try:
            int(v[2:], 16) # Check if the part after 0x is hex
        except ValueError:
            raise ValueError('Invalid Ethereum address format: non-hexadecimal characters found')
        return v

class RevokeAccessRequest(GrantAccessRequest): # Can reuse GrantAccessRequest structure
    pass
