import uuid
import logging # Added import for logging
from typing import List, Optional
from datetime import datetime # Added import for datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.app.crud import crud_audit_log # For audit logging
# Removed: from src.app import models as app_models
from src.app.api.endpoints.auth import get_current_active_user
from src.app.core import security
from src.app.core.blockchain import BlockchainService, get_blockchain_service
# Import the specific ORM model directly
from src.app.models.medical_record import MedicalRecord as MedicalRecordORM
from src.app.core.config import JWT_CONFIG
from src.app.core.database import get_db
from src.app.core.encryption import encrypt_data, decrypt_data, hash_data
from src.app.crud import crud_medical_record
from src.app.models.medical_record import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordDetailResponse,
    RecordType,
    GrantAccessRequest,
    RevokeAccessRequest
)
from src.app.models.user import User, UserRole # Added UserRole

router = APIRouter()

# Import the improved encryption function
from ...core.security_config import get_encryption_key


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
    summary="Get medical records for the current patient, verified against blockchain hashes.",
)
async def get_my_medical_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve medical records for the currently authenticated user (patient).

    This endpoint enhances data integrity by first fetching a list of record hashes
    associated with the patient's Decentralized Identifier (DID) from the blockchain.
    It then retrieves only those records from the local database that match these hashes
    and belong to the authenticated user.

    Args:
        db (Session): SQLAlchemy database session.
        current_user (User): The authenticated user, injected by `get_current_active_user`.
        blockchain_service (BlockchainService): Service for interacting with the blockchain.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return for pagination.

    Returns:
        List[MedicalRecordResponse]: A list of medical records. Returns an empty list if
                                     the user has no DID, the blockchain call fails,
                                     no hashes are found on the blockchain, or no matching
                                     records are found in the database.
    """
    # The user's Decentralized Identifier (DID) is essential for querying blockchain records.
    if not current_user.did:
        logging.warning(f"User {current_user.id} (username: {current_user.username}) has no DID. "
                        "Cannot retrieve blockchain-anchored medical records.")
        return []

    # Fetch record hashes from the blockchain service using the patient's DID.
    # Expects blockchain_service to return a dict: {'success': bool, 'data': {'hashes': [...]}, 'error': str}
    blockchain_response = await blockchain_service.get_record_hashes_for_patient(current_user.did)

    # Handle cases where the blockchain service call was not successful.
    if not blockchain_response.get("success"):
        logging.error(
            f"BlockchainService call to get record hashes failed for patient DID {current_user.did}. "
            f"Error: {blockchain_response.get('error', 'Unknown error')}"
        )
        # Policy: Return empty list on blockchain error to avoid showing potentially stale/incomplete data.
        return []

    # Extract the list of hexadecimal record hashes from the blockchain response.
    record_hashes_hex = blockchain_response.get("data", {}).get("hashes", [])
    if not record_hashes_hex:
        logging.info(f"No medical record hashes found on the blockchain for patient DID {current_user.did}.")
        return []

    retrieved_records = []
    # Iterate through each hash received from the blockchain.
    for record_hash in record_hashes_hex:
        # Query the local database for a medical record that matches the current hash
        # AND belongs to the currently authenticated user (patient_id match).
        # This ensures that even if a hash is associated with the user's DID on-chain,
        # they can only retrieve records they own in the local database.
        db_record = db.query(MedicalRecordORM).filter(
            MedicalRecordORM.data_hash == record_hash,
            MedicalRecordORM.patient_id == current_user.id
        ).first()
        
        if db_record:
            # If a matching and authorized record is found in the database, add it to the list.
            # FastAPI will automatically convert this ORM model to MedicalRecordResponse
            # based on the endpoint's `response_model`.
            retrieved_records.append(db_record)
        else:
            # Log a warning if a hash from the blockchain does not correspond to a valid
            # record in the database for this user. This could indicate data inconsistency
            # (e.g., DB record deleted but blockchain entry remains, or hash mismatch).
            logging.warning(
                f"Medical record with hash {record_hash} found on blockchain for patient {current_user.id} "
                f"(DID: {current_user.did}) but not found in local DB or not matching this patient_id."
            )
    
    # Apply pagination to the final list of verified and retrieved records.
    # This is done after all blockchain hashes have been processed and DB records fetched.
    paginated_records = retrieved_records[skip : skip + limit]
    return paginated_records


@router.get(
    "/{record_id}",
    response_model=MedicalRecordDetailResponse,
    summary="Get a specific medical record with decrypted data",
)
async def get_medical_record_detail(
    record_id: uuid.UUID,
    request: Request, # Added request object
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    blockchain_service: BlockchainService = Depends(get_blockchain_service), 
):
    """
    Retrieve a specific medical record by its ID.
    The raw data will be decrypted if the user is authorized.
    """
    db_record = crud_medical_record.get_medical_record_by_id(db, record_id=record_id)
    ip_address = request.client.host if request.client else "Unknown"

    if not db_record:
        # Log VIEW_RECORD_FAILURE_NOT_FOUND if db_record is None
        # As per task note: If record not found (404), owner_user_id may not be determinable from db_record.
        # For now, assuming db_record is None, we might not have db_record.patient_id.
        # The task mentions focusing on cases where db_record is available for 403/400/503.
        # So, will not add audit log here for 404 to avoid owner_user_id issue without clarification.
        # If logging is strictly required for 404, owner_user_id strategy needs decision (e.g. current_user.id).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found"
        )

    # Authorization logic
    is_owner = (db_record.patient_id == current_user.id)
    can_access = is_owner
    action_type_failure = None
    failure_details = None

    if not is_owner and current_user.role == UserRole.DOCTOR:
        if not current_user.blockchain_address:
            action_type_failure = 'VIEW_RECORD_FAILURE_NO_BC_ADDR'
            failure_details = {"error": "Doctor user does not have a blockchain address configured."}
            crud_audit_log.create_audit_log(
                db=db,
                actor_user_id=current_user.id,
                owner_user_id=db_record.patient_id, # db_record is available here
                record_id=db_record.id,
                action_type=action_type_failure,
                ip_address=ip_address,
                details=failure_details,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=failure_details["error"],
            )
        if not db_record.data_hash:
            action_type_failure = 'VIEW_RECORD_FAILURE_NO_HASH' # Specific action type for no data hash
            failure_details = {"error": "Record cannot be accessed by doctor: No data hash for blockchain verification."}
            crud_audit_log.create_audit_log(
                db=db,
                actor_user_id=current_user.id,
                owner_user_id=db_record.patient_id,
                record_id=db_record.id,
                action_type=action_type_failure,
                ip_address=ip_address,
                details=failure_details,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=failure_details["error"],
            )

        access_check_result = await blockchain_service.check_record_access(
            record_hash_hex=db_record.data_hash,
            accessor_address=current_user.blockchain_address
        )

        if not access_check_result.get("success"):
            action_type_failure = 'VIEW_RECORD_FAILURE_BC_CHECK_FAILED'
            failure_details = {"error": f"Could not verify access on blockchain; access denied. BC Error: {access_check_result.get('error')}"}
            logging.error(f"Blockchain access check failed for doctor {current_user.id} on record {db_record.id}: {access_check_result.get('error')}")
            crud_audit_log.create_audit_log(
                db=db,
                actor_user_id=current_user.id,
                owner_user_id=db_record.patient_id,
                record_id=db_record.id,
                action_type=action_type_failure,
                ip_address=ip_address,
                details=failure_details,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=failure_details["error"],
            )
        
        if access_check_result.get("has_access"):
            can_access = True
        # If has_access is False, can_access remains False (from not is_owner) and will be caught by the next check

    if not can_access:
        action_type_failure = 'VIEW_RECORD_FAILURE_FORBIDDEN'
        failure_details = {"error": "You do not have permission to access this medical record."}
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=db_record.patient_id, # db_record is available
            record_id=db_record.id,
            action_type=action_type_failure,
            ip_address=ip_address,
            details=failure_details,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=failure_details["error"],
        )

    # If can_access is True (either owner or doctor with granted access), proceed to decrypt
    try:
        encryption_key = get_encryption_key()
        decrypted_raw_data = decrypt_data(db_record.encrypted_data, encryption_key)
        
        response_data = MedicalRecordDetailResponse.model_validate(db_record)
        response_data.raw_data = decrypted_raw_data
        
        # Log successful access
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=db_record.patient_id,
            record_id=db_record.id,
            action_type='VIEW_RECORD_SUCCESS',
            ip_address=ip_address,
            details=None, 
        )
        return response_data

    except ValueError as ve: 
        action_type_failure = 'VIEW_RECORD_FAILURE_DECRYPTION'
        failure_details = {"error": f"Failed to decrypt record data. Error: {str(ve)}"}
        logging.error(f"Decryption failed for record {record_id} accessed by user {current_user.id}. Error: {ve}")
        # We log this attempt, but it's an internal server error. Owner ID is from db_record.
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=db_record.patient_id, # db_record is available
            record_id=db_record.id, # record_id from path
            action_type=action_type_failure,
            ip_address=ip_address,
            details=failure_details,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt record data. The data may be corrupted or the key is incorrect.",
        )
    except Exception as e:
        action_type_failure = 'VIEW_RECORD_FAILURE_UNEXPECTED'
        failure_details = {"error": f"An unexpected error occurred: {str(e)}"}
        logging.error(f"Error retrieving medical record detail for {record_id} by user {current_user.id}: {e}")
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=db_record.patient_id, # db_record should be available
            record_id=db_record.id, # record_id from path
            action_type=action_type_failure,
            ip_address=ip_address,
            details=failure_details,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.post(
    "/{record_id}/grant-access",
    summary="Grant access to a medical record",
    status_code=status.HTTP_200_OK, # Or 204 No Content if no body is returned on success
    # response_model=Optional[dict] # Define a suitable response model if needed
)
async def grant_medical_record_access(
    record_id: uuid.UUID,
    access_request: GrantAccessRequest,
    request: Request, # Added request object
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
):
    """
    Grant a specified doctor_address access to a specific medical record on the blockchain.
    The caller must be the owner (patient) of the medical record.
    """
    ip_address = request.client.host if request.client else "Unknown"
    target_doctor_address = access_request.doctor_address # Store for logging consistency

    db_record = crud_medical_record.get_medical_record_by_id(db, record_id=record_id)
    if not db_record:
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id, # Owner not determinable from db_record
            record_id=record_id,
            action_type='GRANT_ACCESS_FAILURE_RECORD_NOT_FOUND',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "Medical record not found"},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found"
        )

    if db_record.patient_id != current_user.id:
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id, # Actor is current_user, owner is also current_user (attempting to act on other's record)
            record_id=record_id,
            action_type='GRANT_ACCESS_FAILURE_FORBIDDEN',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "User does not have permission to grant access to this medical record"},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to grant access to this medical record",
        )

    if not db_record.data_hash: 
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id,
            record_id=record_id,
            action_type='GRANT_ACCESS_FAILURE_NO_HASH', # Specific action type
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "Medical record does not have a data hash; cannot grant access."},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Medical record does not have a data hash; cannot grant access.",
        )

    blockchain_result = await blockchain_service.grant_record_access(
        record_hash_hex=db_record.data_hash,
        doctor_address=target_doctor_address
    )

    if not blockchain_result.get("success"):
        error_detail = blockchain_result.get("error", "Failed to grant access on blockchain.")
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id,
            record_id=record_id,
            action_type='GRANT_ACCESS_FAILURE_BLOCKCHAIN',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": error_detail, "blockchain_error_type": blockchain_result.get("error_type")},
        )
        # Determine status code based on error_type or content if needed
        if "revert" in error_detail.lower() or "NotRecordOwner" in error_detail or \
           "Invalid Ethereum address format" in error_detail:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

    # Log successful grant
    crud_audit_log.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        owner_user_id=current_user.id,
        record_id=record_id,
        action_type='GRANT_ACCESS_SUCCESS',
        ip_address=ip_address,
        target_address=target_doctor_address,
        details={"transaction_hash": blockchain_result.get("transaction_hash")},
    )
    return {
        "message": "Access granted successfully.",
        "record_id": record_id,
        "doctor_address": target_doctor_address,
        "transaction_hash": blockchain_result.get("transaction_hash")
    }


@router.get(
    "/{record_id}/check-access/{accessor_address}",
    summary="Check access to a medical record for a given accessor address",
    status_code=status.HTTP_200_OK,
    # response_model= # Define a Pydantic model for the response, e.g., AccessCheckResponse
)
async def check_medical_record_access(
    record_id: uuid.UUID,
    accessor_address: str, # Path parameter for the address to check
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user), # To verify ownership if needed, or just for consistency
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
):
    """
    Check if a specified accessor_address (e.g., a doctor) has access to a specific
    medical record on the blockchain.

    This endpoint can be called by any authenticated user to check access status,
    but the record itself must exist.
    """
    db_record = crud_medical_record.get_medical_record_by_id(db, record_id=record_id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found"
        )

    # Optional: Add authorization if only specific users (e.g., record owner) can check access.
    # For now, allowing any authenticated user to check access for any existing record.
    # if db_record.patient_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You do not have permission to check access for this medical record",
    #     )
        
    if not db_record.data_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical record does not have a data hash; cannot check access.",
        )

    # Basic validation for accessor_address format (can be enhanced with Web3.is_address)
    if not accessor_address.startswith('0x') or len(accessor_address) != 42:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum address format for accessor."
        )
    try:
        int(accessor_address[2:], 16)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum address format for accessor: non-hexadecimal characters found."
        )


    blockchain_result = await blockchain_service.check_record_access(
        record_hash_hex=db_record.data_hash,
        accessor_address=accessor_address
    )

    if not blockchain_result.get("success"):
        error_detail = blockchain_result.get("error", "Failed to check access on blockchain.")
        if "Invalid Ethereum address format" in error_detail: # From BlockchainService validation
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)
        # Default to 500 for other blockchain related errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

    return {
        "record_id": record_id,
        "accessor_address": accessor_address,
        "has_access": blockchain_result.get("has_access"),
        "checked_at": datetime.utcnow().isoformat() # Optional: add a timestamp for the check
    }


@router.post(
    "/{record_id}/revoke-access",
    summary="Revoke access to a medical record",
    status_code=status.HTTP_200_OK,
    # response_model=Optional[dict] # Define a suitable response model if needed
)
async def revoke_medical_record_access(
    record_id: uuid.UUID,
    access_request: RevokeAccessRequest, # Uses RevokeAccessRequest
    request: Request, # Added request object
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
):
    """
    Revoke a specified doctor_address access to a specific medical record on the blockchain.
    The caller must be the owner (patient) of the medical record.
    """
    ip_address = request.client.host if request.client else "Unknown"
    target_doctor_address = access_request.doctor_address # Store for logging consistency

    db_record = crud_medical_record.get_medical_record_by_id(db, record_id=record_id)
    if not db_record:
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id, # Owner not determinable from db_record
            record_id=record_id,
            action_type='REVOKE_ACCESS_FAILURE_RECORD_NOT_FOUND',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "Medical record not found"},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found"
        )

    if db_record.patient_id != current_user.id:
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id, # Actor is current_user
            record_id=record_id,
            action_type='REVOKE_ACCESS_FAILURE_FORBIDDEN',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "User does not have permission to revoke access to this medical record"},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to revoke access to this medical record",
        )

    if not db_record.data_hash:
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id,
            record_id=record_id,
            action_type='REVOKE_ACCESS_FAILURE_NO_HASH',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": "Medical record does not have a data hash; cannot revoke access."},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical record does not have a data hash; cannot revoke access.",
        )

    blockchain_result = await blockchain_service.revoke_record_access( 
        record_hash_hex=db_record.data_hash,
        doctor_address=target_doctor_address
    )

    if not blockchain_result.get("success"):
        error_detail = blockchain_result.get("error", "Failed to revoke access on blockchain.")
        crud_audit_log.create_audit_log(
            db=db,
            actor_user_id=current_user.id,
            owner_user_id=current_user.id,
            record_id=record_id,
            action_type='REVOKE_ACCESS_FAILURE_BLOCKCHAIN',
            ip_address=ip_address,
            target_address=target_doctor_address,
            details={"error": error_detail, "blockchain_error_type": blockchain_result.get("error_type")},
        )
        if "revert" in error_detail.lower() or "NotRecordOwner" in error_detail or \
           "Invalid Ethereum address format" in error_detail:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

    # Log successful revoke
    crud_audit_log.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        owner_user_id=current_user.id,
        record_id=record_id,
        action_type='REVOKE_ACCESS_SUCCESS',
        ip_address=ip_address,
        target_address=target_doctor_address,
        details={"transaction_hash": blockchain_result.get("transaction_hash")},
    )
    return {
        "message": "Access revoked successfully.",
        "record_id": record_id,
        "doctor_address": target_doctor_address,
        "transaction_hash": blockchain_result.get("transaction_hash")
    }
