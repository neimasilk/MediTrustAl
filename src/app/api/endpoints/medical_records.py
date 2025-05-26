import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.api.endpoints.auth import get_current_active_user # Corrected import
from src.app.core import security # For potential future use, not directly for key
from src.app.core.blockchain import BlockchainService, get_blockchain_service
from src.app.core.config import JWT_CONFIG # For encryption key
from src.app.core.database import get_db
from src.app.core.encryption import encrypt_data, decrypt_data, hash_data
from src.app.crud import crud_medical_record
from src.app.models.medical_record import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordDetailResponse,
    RecordType
)
from src.app.models.user import User

router = APIRouter()

def get_encryption_key() -> bytes:
    """
    Derives a 32-byte encryption key from the JWT secret key.
    This is a placeholder/MVP approach. In a real system, use a dedicated key management service.
    """
    jwt_secret = JWT_CONFIG.get("secret_key", "default-fallback-secret-key-for-encryption") # Fallback for safety
    if len(jwt_secret) >= 32:
        return jwt_secret[:32].encode('utf-8')
    else:
        # Pad the key if it's shorter than 32 bytes
        return (jwt_secret + '0'*(32-len(jwt_secret))).encode('utf-8')


@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical record",
)
async def create_medical_record_endpoint(
    medical_record_in: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user), # Corrected dependency
    blockchain_service: BlockchainService = Depends(get_blockchain_service), 
):
    """
    Create a new medical record for the currently authenticated user.

    The raw data of the record will be encrypted before storage.
    A hash of the raw data will be stored on the blockchain.
    """
    patient_id = current_user.id
    patient_did = current_user.did

    if not patient_did:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user does not have a Decentralized Identifier (DID) associated. Cannot create blockchain-anchored record.",
        )

    try:
        encryption_key = get_encryption_key()
        
        # Encrypt raw_data
        encrypted_blob = encrypt_data(medical_record_in.raw_data, encryption_key)
        
        # Hash raw_data (before encryption)
        raw_data_hash = hash_data(medical_record_in.raw_data)

        # Create DB record
        # The CRUD function create_medical_record handles mapping medical_record_in.metadata to record_metadata
        new_db_record = crud_medical_record.create_medical_record(
            db=db,
            medical_record_in=medical_record_in,
            patient_id=patient_id,
            encrypted_data=encrypted_blob,
            data_hash=raw_data_hash,
        )

        # Add hash to blockchain
        # Ensure record_type is passed as string value if that's what blockchain expects
        blockchain_result = await blockchain_service.add_medical_record_hash(
            record_hash_hex=new_db_record.data_hash, # Use the hash stored in DB
            patient_did=patient_did,
            record_type=new_db_record.record_type.value, # Pass enum's value
        )

        if blockchain_result.get("success"):
            tx_hash = blockchain_result.get("transaction_hash")
            if tx_hash: # Ensure tx_hash is not None before updating
                updated_record = crud_medical_record.update_medical_record_blockchain_id(
                    db=db, record_id=new_db_record.id, blockchain_tx_hash=tx_hash
                )
                # If update was successful and returned a record, use it.
                # Otherwise, new_db_record (which was refreshed after create) is the fallback.
                if updated_record:
                    return updated_record # Return the record with the blockchain_id from update
            # If tx_hash was None or update failed to return record, new_db_record (refreshed after creation) is used.
            # new_db_record at this point does not have blockchain_id if success was True but tx_hash was missing.
            # Fall through to return new_db_record, which should have None for blockchain_id in this specific sub-path.

        # If blockchain call was not successful, or if it was successful but tx_hash was missing,
        # we return the record as it was created (blockchain_id should be None or its initial state).
        # Ensure new_db_record is the latest state from DB before returning if no update happened or if update path didn't return.
        db.refresh(new_db_record) # Refresh to be sure, especially if update_medical_record_blockchain_id doesn't refresh the original instance.
        return new_db_record

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Log the exception for debugging
        print(f"Error creating medical record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating the medical record: {str(e)}",
        )


@router.get(
    "/patient/me",
    response_model=List[MedicalRecordResponse],
    summary="Get medical records for the current patient",
)
async def get_my_medical_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user), # Corrected dependency
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all medical records for the currently authenticated user (patient).
    """
    records = crud_medical_record.get_medical_records_by_patient_id(
        db, patient_id=current_user.id, skip=skip, limit=limit
    )
    return records


@router.get(
    "/{record_id}",
    response_model=MedicalRecordDetailResponse,
    summary="Get a specific medical record with decrypted data",
)
async def get_medical_record_detail(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user), # Corrected dependency
):
    """
    Retrieve a specific medical record by its ID.
    The raw data will be decrypted if the user is authorized.
    """
    db_record = crud_medical_record.get_medical_record_by_id(db, record_id=record_id)

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found"
        )

    # Authorization: Only the patient themselves can access the detailed record
    # Future: Extend this for authorized healthcare providers
    if db_record.patient_id != current_user.id:
        # Add role check here if non-patients (e.g. doctors) should be able to access
        # For now, strict patient-only access to decrypted data
        # if current_user.role != UserRole.DOCTOR: # Assuming UserRole enum and role field on User model
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this medical record",
        )

    try:
        encryption_key = get_encryption_key()
        decrypted_raw_data = decrypt_data(db_record.encrypted_data, encryption_key)
        
        # Create the response object, including the decrypted raw_data
        # Pydantic's from_orm will map fields from db_record to MedicalRecordDetailResponse
        # We then set raw_data manually
        response_data = MedicalRecordDetailResponse.model_validate(db_record)
        response_data.raw_data = decrypted_raw_data
        
        return response_data

    except ValueError as ve: # Catches decryption errors like InvalidTag, corrupted data, or wrong key
        # Log the error for auditing/security purposes
        print(f"Decryption failed for record {record_id} accessed by user {current_user.id}. Error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt record data. The data may be corrupted or the key is incorrect.",
        )
    except Exception as e:
        print(f"Error retrieving medical record detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
