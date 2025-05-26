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


class MedicalRecordResponse(MedicalRecordBase):
    id: uuid.UUID
    patient_id: uuid.UUID
    blockchain_record_id: Optional[str] = None
    data_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        exclude = {"raw_data"}

    # Custom serialization to exclude raw_data
    def model_dump(self, *args, **kwargs):
        kwargs.setdefault('exclude', {'raw_data'})
        return super().model_dump(*args, **kwargs)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Manually exclude 'raw_data' if present in the input object
        if hasattr(obj, 'raw_data') and 'raw_data' not in kwargs.get('exclude', {}):
            if kwargs.get('exclude') is None:
                 kwargs['exclude'] = {'raw_data'}
            else:
                 kwargs['exclude'].add('raw_data')
        return super().model_validate(obj, *args, **kwargs)


class MedicalRecordDetailResponse(MedicalRecordResponse):
    raw_data: Optional[str] = None

    # Override model_dump to include raw_data by default for this specific model
    def model_dump(self, *args, **kwargs):
        # Ensure 'raw_data' is not in the default exclude set for this class
        if 'exclude' in kwargs and kwargs['exclude'] is not None and 'raw_data' in kwargs['exclude']:
            # Create a mutable copy if it's a tuple or set
            if isinstance(kwargs['exclude'], (set, frozenset)):
                kwargs['exclude'] = set(kwargs['exclude'])
                kwargs['exclude'].remove('raw_data')
            elif isinstance(kwargs['exclude'], tuple):
                new_exclude = list(kwargs['exclude'])
                if 'raw_data' in new_exclude:
                    new_exclude.remove('raw_data')
                kwargs['exclude'] = tuple(new_exclude)
        
        # If exclude is not set, or raw_data was removed, proceed normally
        return super(MedicalRecordResponse, self).model_dump(*args, **kwargs)

    # No need to override model_validate unless specific input processing for raw_data is needed
    # The parent's model_validate will handle exclusion if raw_data is explicitly excluded during validation.
    # For response model, we primarily care about output (model_dump).
