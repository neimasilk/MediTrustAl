import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.app.models.medical_record import MedicalRecord, MedicalRecordCreate


def create_medical_record(
    db: Session,
    *,
    medical_record_in: MedicalRecordCreate,
    patient_id: uuid.UUID,
    encrypted_data: bytes,
    data_hash: str,
) -> MedicalRecord:
    """
    Create a new medical record.
    """
    db_obj = MedicalRecord(
        patient_id=patient_id,
        record_type=medical_record_in.record_type,
        record_metadata=medical_record_in.record_metadata,
        encrypted_data=encrypted_data,
        data_hash=data_hash,
        blockchain_record_id=None,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_medical_record_by_id(
    db: Session, record_id: uuid.UUID
) -> Optional[MedicalRecord]:
    """
    Get a medical record by its ID.
    """
    return (
        db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    )


def get_medical_records_by_patient_id(
    db: Session, patient_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[MedicalRecord]:
    """
    Get all medical records for a specific patient.
    """
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_medical_record_blockchain_id(
    db: Session, record_id: uuid.UUID, blockchain_tx_hash: str
) -> Optional[MedicalRecord]:
    """
    Update the blockchain transaction hash for a medical record.
    """
    db_obj = get_medical_record_by_id(db, record_id)
    if db_obj:
        db_obj.blockchain_record_id = blockchain_tx_hash
        db.commit()
        db.refresh(db_obj)
    return db_obj
