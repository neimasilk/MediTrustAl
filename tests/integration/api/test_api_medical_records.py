import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock # Added MagicMock

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.core.config import JWT_CONFIG # For deriving encryption key
from src.app.core.encryption import encrypt_data, decrypt_data, hash_data
from src.app.core.security_config import get_encryption_key
from src.app.crud import crud_user, crud_medical_record
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserRole
from src.app.models.medical_record import MedicalRecord, MedicalRecordCreate, RecordType, MedicalRecordDetailResponse, MedicalRecordResponse
from src.app.main import app # To ensure app context for client
from src.app.core.blockchain import get_blockchain_service # Import for overriding

# Use the same encryption key function as the main application
TEST_ENCRYPTION_KEY = get_encryption_key()

# Fixture to create a user and get an auth token
@pytest.fixture
def authenticated_patient_token(client: TestClient, db_session: Session):
    # Register user via API
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"patient_records_fixture_{unique_suffix}@example.com"
    username = f"pat_rec_fix_{unique_suffix}"
    password = "testpassword_fixture"
    full_name = "Patient Records Fixture User"
    
    registration_payload = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": UserRole.PATIENT.value # Ensure role is passed as string value
    }
    
    reg_response = client.post("/api/v1/auth/register", json=registration_payload)
    assert reg_response.status_code == status.HTTP_201_CREATED, \
        f"Fixture user registration failed: {reg_response.json()}"
    registered_user_data = reg_response.json()
    
    # Log in to get token
    login_data = {"username": username, "password": password}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK, \
        f"Fixture user login failed: {login_response.json()}"
    
    token_data = login_response.json()
    
    # The /auth/register endpoint (if it uses crud_user.create_user) should return a UserResponse
    # which contains the user's ID and DID (if generated and stored by crud_user.create_user)
    # We need user_id (UUID) and user_did (string)
    # The `registered_user_data` comes from UserResponse model which has id: uuid.UUID
    # The `did` is not directly part of UserResponse, it's on the ORM model.
    # We need to fetch the user from DB to get the DID for blockchain calls if not in response.
    # For now, let's assume crud_user.create_user correctly populates DID and it's available
    # via some mechanism or we mock it for blockchain part of tests.
    # The /users/me endpoint can give us the current user's details including DID.
    
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK, \
        f"Failed to get user details for fixture: {me_response.json()}"
    user_details_from_me = me_response.json()
    # The /users/me endpoint returns a UserResponse model, which now includes full_name and role
    # The User ORM model has 'did'. UserResponse does not.
    # We need to fetch the user from DB to get the DID for blockchain calls.
    
    # Fetch user from DB to get DID, as UserResponse doesn't include it.
    # This is a bit circular if create_user in auth doesn't return it.
    # The UserResponse model from user.py has id: uuid.UUID.
    # The /api/v1/auth/register returns UserResponse
    # The /api/v1/users/me returns UserResponse (this is a custom UserResponse in users.py, not the Pydantic one)

    # Let's check the UserResponse from users.py
    # It's defined as: class UserResponse(BaseModel): user_id: str, role: str, is_registered: bool
    # This is NOT the Pydantic UserResponse from models/user.py
    # This will be an issue. The /users/me endpoint should use models.user.UserResponse

    # For now, let's assume the DID is needed and we can get it.
    # The crucial part is the token and user_id.
    # The `patient_did` for `add_medical_record_hash` comes from `current_user.did`
    # `current_user` is the ORM User model.
    
    # The `registered_user_data['id']` is from `UserResponse.id` which is uuid.UUID
    # The `user_details_from_me['user_id']` is from the custom UserResponse in users.py, which is `user_id: str`
    # This implies user_details_from_me['user_id'] is the DID.

    # Let's get the user_id (UUID) from the registration response for DB lookups
    user_id_from_reg = registered_user_data["id"] # This is a UUID string from UserResponse (FastAPI converts UUID to str)
    
    # To get the DID, we'd typically query the DB using user_id_from_reg or rely on /users/me if it provided it.
    # The current /users/me returns user_id as the DID.
    user_did_from_me = user_details_from_me["did"] # This is the DID string

    return {
        "token": token_data["access_token"], 
        "user_id": uuid.UUID(user_id_from_reg), # Convert string UUID back to UUID object for internal test consistency
        "user_did": user_did_from_me, # This should be the DID string
        "blockchain_address": None # Patients don't have a blockchain_address in this model yet
    }


# --- POST /api/v1/medical-records/ ---

def test_create_medical_record_success(
    client: TestClient, authenticated_patient_token, db_session: Session
):
    mock_blockchain_service_instance = AsyncMock()
    mock_blockchain_service_instance.add_medical_record_hash.return_value = {
        "success": True,
        "transaction_hash": "0xmock_tx_hash_success"
    }
    
    def override_get_blockchain_service():
        return mock_blockchain_service_instance

    app.dependency_overrides[get_blockchain_service] = override_get_blockchain_service

    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    raw_data_content = "Initial consultation notes: Patient reports mild headache."
    record_data = {
        "record_type": RecordType.MEDICAL_HISTORY.value,
        "record_metadata": {"source": "patient_report"},
        "raw_data": raw_data_content
    }
    
    response = client.post("/api/v1/medical-records/", headers=headers, json=record_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    created_record_data = response.json()
    assert created_record_data["patient_id"] == str(authenticated_patient_token["user_id"])
    assert created_record_data["record_type"] == RecordType.MEDICAL_HISTORY.value
    assert created_record_data["record_metadata"] == {"source": "patient_report"}
    assert "raw_data" not in created_record_data # MedicalRecordResponse excludes raw_data

    # Debug: Directly check the database
    db_record_direct_check = db_session.query(MedicalRecord).filter(MedicalRecord.id == uuid.UUID(created_record_data["id"])).first()

    assert created_record_data["blockchain_record_id"] == "0xmock_tx_hash_success"

    # Verify in DB
    db_record = crud_medical_record.get_medical_record_by_id(db_session, record_id=uuid.UUID(created_record_data["id"]))
    assert db_record is not None
    assert db_record.patient_id == authenticated_patient_token["user_id"]
    assert db_record.record_metadata == {"source": "patient_report"} 
    assert db_record.data_hash == hash_data(raw_data_content)
    assert db_record.blockchain_record_id == "0xmock_tx_hash_success"
    
    decrypted_db_data = decrypt_data(db_record.encrypted_data, TEST_ENCRYPTION_KEY)
    assert decrypted_db_data == raw_data_content

    mock_blockchain_service_instance.add_medical_record_hash.assert_called_once_with(
        record_hash_hex=db_record.data_hash,
        patient_did=authenticated_patient_token["user_did"],
        record_type=RecordType.MEDICAL_HISTORY.value
    )
    # Clean up the override after the test
    del app.dependency_overrides[get_blockchain_service]

def test_create_medical_record_blockchain_failure(
    client: TestClient, authenticated_patient_token, db_session: Session
):
    mock_blockchain_service_instance = AsyncMock()
    mock_blockchain_service_instance.add_medical_record_hash.return_value = {
        "success": False,
        "error": "Blockchain network timeout"
    }

    def override_get_blockchain_service():
        return mock_blockchain_service_instance

    app.dependency_overrides[get_blockchain_service] = override_get_blockchain_service

    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    raw_data_content = "Follow-up: Headache persists."
    record_data = {
        "record_type": RecordType.DIAGNOSIS.value,
        "record_metadata": {"physician": "Dr. Cura"},
        "raw_data": raw_data_content
    }
    
    response = client.post("/api/v1/medical-records/", headers=headers, json=record_data)
    
    assert response.status_code == status.HTTP_201_CREATED 
    created_record_data = response.json()

    # Debug: Directly check the database
    db_record_direct_check_fail = db_session.query(MedicalRecord).filter(MedicalRecord.id == uuid.UUID(created_record_data["id"])).first()

    assert created_record_data["blockchain_record_id"] is None 

    # Verify in DB
    db_record = crud_medical_record.get_medical_record_by_id(db_session, record_id=uuid.UUID(created_record_data["id"]))
    assert db_record is not None
    assert db_record.blockchain_record_id is None
    
    # Clean up the override after the test
    del app.dependency_overrides[get_blockchain_service]

def test_create_medical_record_invalid_input(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Missing raw_data
    invalid_data = {"record_type": RecordType.LAB_RESULT.value}
    response = client.post("/api/v1/medical-records/", headers=headers, json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid record_type
    invalid_data_type = {"record_type": "INVALID_TYPE", "raw_data": "test"}
    response = client.post("/api/v1/medical-records/", headers=headers, json=invalid_data_type)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# --- GET /api/v1/medical-records/patient/me ---

# Scenario 1: Patient has records on blockchain and matching records in DB. (Updates existing test)
def test_get_my_medical_records_scenario1_blockchain_match(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    user_did = authenticated_patient_token["user_did"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create some records for this user
    raw1 = "My record 1 for blockchain match"
    record1 = crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.PRESCRIPTION, raw_data=raw1, record_metadata={"note":"r1"}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw1, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw1)
    )
    raw2 = "My record 2 for blockchain match"
    record2 = crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.VACCINATION, raw_data=raw2, record_metadata={"note":"r2"}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw2, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw2)
    )
    db_session.commit() # Ensure records are committed

    # Configure blockchain service mock
    blockchain_service_mock = get_blockchain_service()
    blockchain_service_mock.get_record_hashes_for_patient.return_value = {
        "success": True,
        "data": {"hashes": [record1.data_hash, record2.data_hash]}
    }

    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records_response = response.json()
    assert len(records_response) == 2
    
    # Verify the content of returned records (order might not be guaranteed, so check presence)
    response_hashes = {r["data_hash"] for r in records_response}
    assert record1.data_hash in response_hashes
    assert record2.data_hash in response_hashes
    for r_data in records_response:
        assert r_data["patient_id"] == str(user_id)
        assert "raw_data" not in r_data # MedicalRecordResponse should not have raw_data
        if r_data["data_hash"] == record1.data_hash:
            assert r_data["record_metadata"] == {"note":"r1"}
        elif r_data["data_hash"] == record2.data_hash:
            assert r_data["record_metadata"] == {"note":"r2"}


# Scenario 2: Patient has records on blockchain, but some/none have matching, authorized records in DB.
def test_get_my_medical_records_scenario2_partial_or_no_db_match(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    user_did = authenticated_patient_token["user_did"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record that exists in DB and belongs to the user
    raw_existing = "Existing record for partial match"
    existing_record = crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.LAB_RESULT, raw_data=raw_existing, record_metadata={"status":"final"}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw_existing, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw_existing)
    )
    
    # Record for another user (to simulate unauthorized hash if it were on blockchain for current user)
    # This part is more about ensuring our DB query correctly filters by patient_id
    other_user_raw = "Other user's record"
    # We need another user for this. The fixture `authenticated_patient_token` could be called again for a new user, or create one manually.
    # For simplicity, we'll just use a hash that's "on blockchain" but doesn't match our current user's records.
    
    hash_for_current_user_not_in_db = hash_data("A record not in DB for current user")
    hash_of_existing_record = existing_record.data_hash
    
    db_session.commit()

    blockchain_service_mock = get_blockchain_service()
    blockchain_service_mock.get_record_hashes_for_patient.return_value = {
        "success": True,
        "data": {"hashes": [hash_of_existing_record, hash_for_current_user_not_in_db]}
    }

    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records_response = response.json()
    assert len(records_response) == 1 # Only the existing_record should be returned
    assert records_response[0]["data_hash"] == hash_of_existing_record
    assert records_response[0]["patient_id"] == str(user_id)


# Scenario 3: Patient has no records on blockchain. (Updates existing test_get_my_medical_records_no_records)
def test_get_my_medical_records_scenario3_no_blockchain_records(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_did = authenticated_patient_token["user_did"] # Though not strictly needed if no records are created
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure DB might have records, but blockchain says none
    user_id = authenticated_patient_token["user_id"]
    raw_db_only = "DB record not on blockchain list"
    crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.DIAGNOSIS, raw_data=raw_db_only, record_metadata={}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw_db_only, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw_db_only)
    )
    db_session.commit()
    
    blockchain_service_mock = get_blockchain_service()
    blockchain_service_mock.get_record_hashes_for_patient.return_value = {
        "success": True,
        "data": {"hashes": []} # Empty list from blockchain
    }
    
    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records_response = response.json()
    assert len(records_response) == 0


# Scenario 4: Blockchain service returns an error.
def test_get_my_medical_records_scenario4_blockchain_service_error(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_did = authenticated_patient_token["user_did"]
    headers = {"Authorization": f"Bearer {token}"}

    blockchain_service_mock = get_blockchain_service()
    blockchain_service_mock.get_record_hashes_for_patient.return_value = {
        "success": False,
        "error": "Blockchain communication error"
    }

    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK # Current endpoint returns [] on error
    records_response = response.json()
    assert len(records_response) == 0


# Scenario 5: Pagination.
def test_get_my_medical_records_scenario5_pagination(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    user_did = authenticated_patient_token["user_did"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple records
    record_hashes_in_order = []
    for i in range(3):
        raw_data = f"Paginated record {i+1}"
        record = crud_medical_record.create_medical_record(
            db_session,
            medical_record_in=MedicalRecordCreate(record_type=RecordType.MEDICAL_HISTORY, raw_data=raw_data, record_metadata={"index": i}),
            patient_id=user_id,
            encrypted_data=encrypt_data(raw_data, TEST_ENCRYPTION_KEY),
            data_hash=hash_data(raw_data)
        )
        record_hashes_in_order.append(record.data_hash)
    db_session.commit()

    blockchain_service_mock = get_blockchain_service()
    # The order of hashes from blockchain might not be guaranteed, but the DB records have timestamps.
    # The endpoint logic currently sorts by nothing specific if hashes are out of order from DB.
    # For stable pagination test, ensure the hashes returned from blockchain are in a specific order
    # if the DB retrieval order by those hashes is what we want to test.
    # However, the code iterates hashes and appends to a list. The final list order depends on blockchain hash order.
    # Let's assume the order of hashes from blockchain is record_hashes_in_order for this test.
    blockchain_service_mock.get_record_hashes_for_patient.return_value = {
        "success": True,
        "data": {"hashes": record_hashes_in_order} 
    }

    # Test skip=1, limit=1 (get the second record)
    response = client.get("/api/v1/medical-records/patient/me?skip=1&limit=1", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records_response = response.json()
    assert len(records_response) == 1
    assert records_response[0]["data_hash"] == record_hashes_in_order[1] # Check it's the second record
    assert records_response[0]["record_metadata"] == {"index": 1}


# --- GET /api/v1/medical-records/{record_id} ---

# Fixture for a doctor user with a known blockchain address
@pytest.fixture
def authenticated_doctor_token(client: TestClient, db_session: Session):
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"doctor_fixture_{unique_suffix}@example.com"
    username = f"doc_fix_{unique_suffix}"
    password = "doctorpassword_fixture"
    full_name = "Doctor Fixture User"
    doctor_blockchain_address = f"0xDoctor{unique_suffix[:34]}" # Ensure it's 42 chars

    # Create doctor user directly in DB to set blockchain_address
    # as register endpoint might not support setting it.
    user_in_db = crud_user.get_user_by_email(db_session, email=email)
    if user_in_db: # Should not happen with unique_suffix, but good practice
        db_session.delete(user_in_db)
        db_session.commit()

    user_create = UserCreate(
        email=email, 
        username=username, 
        password=password, 
        full_name=full_name, 
        role=UserRole.DOCTOR, 
        # did=f"did:example:doctor:{unique_suffix}" # Doctors might also have DIDs
    )
    doctor_did = f"did:example:doctor:{unique_suffix}"
    # Manually set blockchain_address as UserCreate doesn't have it
    db_user = crud_user.create_user(db_session, user_in=user_create, did=doctor_did)
    db_user.blockchain_address = doctor_blockchain_address
    # db_user.did = f"did:example:doctor:{unique_suffix}" # DID is now set during creation
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    
    login_data = {"username": username, "password": password}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    token_data = login_response.json()

    return {
        "token": token_data["access_token"],
        "user_id": db_user.id, # UUID object
        "user_did": doctor_did, # Use the variable that was passed
        "blockchain_address": db_user.blockchain_address # string
    }


def test_get_medical_record_detail_success_patient_owner(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    raw_data_content = "Detailed vital signs: BP 120/80, HR 70."
    # Ensure the mock for blockchain service is NOT active for this owner-based access test,
    # or ensure check_record_access is not called for owners.
    # For simplicity, we can remove the override if it was set globally by another test,
    # or ensure this test runs before those that override it globally.
    # The endpoint logic should bypass blockchain check for owner.
    if get_blockchain_service in app.dependency_overrides:
        del app.dependency_overrides[get_blockchain_service]


    created_db_record = crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.VITAL_SIGNS, raw_data=raw_data_content, record_metadata={"device":"Oximeter"}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw_data_content) # Ensure data_hash is set
    )
    record_id = created_db_record.id
    db_session.commit()
    db_session.refresh(created_db_record)

    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    record_detail = response.json()
    validated_detail = MedicalRecordDetailResponse.model_validate(record_detail)

    assert validated_detail.id == record_id
    assert validated_detail.patient_id == user_id
    assert validated_detail.record_type == RecordType.VITAL_SIGNS
    assert validated_detail.record_metadata == {"device":"Oximeter"}
    assert validated_detail.raw_data == raw_data_content

    # Get fresh record from database to avoid DetachedInstanceError
    db_record = crud_medical_record.get_medical_record_by_id(db_session, record_id=record_id)
    assert db_record is not None
    assert db_record.patient_id == user_id
    assert db_record.record_metadata == {"device":"Oximeter"}
    assert db_record.data_hash == hash_data(raw_data_content)
    # blockchain_record_id should be None since we're not actually calling blockchain service in this test
    assert db_record.blockchain_record_id is None
    
    # Verify encryption
    decrypted_db_data = decrypt_data(db_record.encrypted_data, TEST_ENCRYPTION_KEY)
    assert decrypted_db_data == raw_data_content

def test_get_medical_record_detail_not_found(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    non_existent_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/medical-records/{non_existent_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_medical_record_detail_forbidden(client: TestClient, authenticated_patient_token, db_session: Session):
    # Create a record for another user
    # Create a record for another user
    other_unique_suffix = uuid.uuid4().hex[:8]
    other_user_email = f"other_patient_fixture_{other_unique_suffix}@example.com"
    other_user_username = f"other_user_fix_{other_unique_suffix}"
    other_user_password = "other_password_fixture"
    other_user_full_name = "Other Fixture User"

    other_reg_payload = {
        "email": other_user_email,
        "username": other_user_username,
        "password": other_user_password,
        "full_name": other_user_full_name,
        "role": UserRole.PATIENT.value
    }
    other_reg_response = client.post("/api/v1/auth/register", json=other_reg_payload)
    assert other_reg_response.status_code == status.HTTP_201_CREATED, \
        f"Other user registration failed: {other_reg_response.json()}"
    other_db_user_id = uuid.UUID(other_reg_response.json()["id"]) # Get ID of the other user
    
    other_user_raw_data = "Confidential data for other user"
    # Create record directly via CRUD for this other user
    other_record = crud_medical_record.create_medical_record(
        db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.DIAGNOSIS, raw_data=other_user_raw_data, record_metadata={"access_level": "restricted"}),
        patient_id=other_db_user_id,
        encrypted_data=encrypt_data(other_user_raw_data, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(other_user_raw_data)
    )
    
    # Try to access it with authenticated_patient_token (PATIENT accessing OTHER PATIENT's record)
    token = authenticated_patient_token["token"] 
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/medical-records/{other_record.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN # Patient cannot access other patient's record

def test_get_medical_record_detail_malformed_uuid(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    malformed_id = "not-a-uuid"
    
    response = client.get(f"/api/v1/medical-records/{malformed_id}", headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch('src.app.api.endpoints.medical_records.decrypt_data')
def test_get_medical_record_detail_decryption_failure(
    mock_decrypt_data, client: TestClient, authenticated_patient_token, db_session: Session
):
    mock_decrypt_data.side_effect = ValueError("Decryption failed. Data may be corrupted or key is incorrect.")
    
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    raw_data_content = "Data that will fail decryption"
    # Ensure record has data_hash
    record_data_hash = hash_data(raw_data_content)
    created_db_record = crud_medical_record.create_medical_record(
        db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.LAB_RESULT, raw_data=raw_data_content, record_metadata={"sample_id": "S123"}),
        patient_id=user_id,
        encrypted_data=encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY),
        data_hash=record_data_hash 
    )
    record_id = created_db_record.id
    db_session.commit()
    db_session.refresh(created_db_record)

    encrypted_data_val = created_db_record.encrypted_data

    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to decrypt record data" in response.json()["detail"]
    mock_decrypt_data.assert_called_once_with(encrypted_data_val, TEST_ENCRYPTION_KEY)


# --- Doctor Access Tests for GET /api/v1/medical-records/{record_id} ---

def test_get_medical_record_detail_doctor_access_granted(
    client: TestClient, authenticated_doctor_token, created_record_for_access_tests, db_session: Session
):
    doctor_token = authenticated_doctor_token["token"]
    doctor_address = authenticated_doctor_token["blockchain_address"]
    record_id = created_record_for_access_tests["id"]
    record_data_hash = created_record_for_access_tests["data_hash"] # from the patient's record
    headers = {"Authorization": f"Bearer {doctor_token}"}

    mock_bs_for_check = AsyncMock()
    mock_bs_for_check.check_record_access.return_value = {"success": True, "has_access": True}
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_check
    
    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(record_id)
    assert "raw_data" in response_data # Doctor should get decrypted data

    mock_bs_for_check.check_record_access.assert_called_once_with(
        record_hash_hex=record_data_hash,
        accessor_address=doctor_address
    )
    del app.dependency_overrides[get_blockchain_service]


def test_get_medical_record_detail_doctor_access_denied_blockchain(
    client: TestClient, authenticated_doctor_token, created_record_for_access_tests, db_session: Session
):
    doctor_token = authenticated_doctor_token["token"]
    doctor_address = authenticated_doctor_token["blockchain_address"]
    record_id = created_record_for_access_tests["id"]
    headers = {"Authorization": f"Bearer {doctor_token}"}

    mock_bs_for_check = AsyncMock()
    mock_bs_for_check.check_record_access.return_value = {"success": True, "has_access": False} # Access explicitly denied
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_check
    
    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    del app.dependency_overrides[get_blockchain_service]


def test_get_medical_record_detail_doctor_blockchain_check_fails(
    client: TestClient, authenticated_doctor_token, created_record_for_access_tests, db_session: Session
):
    doctor_token = authenticated_doctor_token["token"]
    record_id = created_record_for_access_tests["id"]
    headers = {"Authorization": f"Bearer {doctor_token}"}

    mock_bs_for_check = AsyncMock()
    mock_bs_for_check.check_record_access.return_value = {"success": False, "error": "Network error"} # Blockchain call fails
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_check
    
    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE # Or 403 as per current code
    del app.dependency_overrides[get_blockchain_service]


def test_get_medical_record_detail_doctor_no_blockchain_address(
    client: TestClient, authenticated_doctor_token, created_record_for_access_tests, db_session: Session
):
    # Modify doctor user to have no blockchain_address
    doctor_user_id = authenticated_doctor_token["user_id"]
    db_doctor_user = crud_user.get_user_by_id(db_session, user_id=doctor_user_id) # Corrected function name
    assert db_doctor_user is not None, "Doctor user not found in DB for modification"
    db_doctor_user.blockchain_address = None
    db_session.add(db_doctor_user)
    db_session.commit()

    doctor_token = authenticated_doctor_token["token"]
    record_id = created_record_for_access_tests["id"]
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST # Or 403
    assert "Doctor user does not have a blockchain address configured" in response.json()["detail"]


def test_get_medical_record_detail_doctor_record_no_data_hash(
    client: TestClient, authenticated_doctor_token, created_record_for_access_tests, db_session: Session
):
    # Modify record to have no data_hash
    record_id = created_record_for_access_tests["id"]
    # The endpoint `get_medical_record_detail` fetches its own copy, so this won't work.
    # The proper way is to ensure the record is created without a data_hash IF that's a valid state,
    # or mock the return of `get_medical_record_by_id`.
    # Since `data_hash` is NOT NULL, we cannot create it as None.
    # So, we must mock the `crud_medical_record.get_medical_record_by_id` call.

    # Re-approach: Mock the crud function to return a simple MagicMock with data_hash = None
    
    patient_owner_id = created_record_for_access_tests["owner_id"] # The actual owner (patient)

    # Create a MagicMock for the record, setting attributes via constructor
    mock_record_object = MagicMock(
        id=record_id,
        patient_id=patient_owner_id, # Ensure it's not the doctor's ID for is_owner check
        data_hash=None # Explicitly set data_hash to None
    )

    # Mock blockchain_service to ensure check_record_access is NOT called
    mock_bs_for_no_hash_test = AsyncMock()
    mock_bs_for_no_hash_test.check_record_access.side_effect = AssertionError("check_record_access should not have been called in no_data_hash test")
    
    original_bs_override = app.dependency_overrides.get(get_blockchain_service)
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_no_hash_test

    try:
        # Patch the CRUD function to return this simple mock
        with patch('src.app.api.endpoints.medical_records.crud_medical_record.get_medical_record_by_id', return_value=mock_record_object):
            doctor_token = authenticated_doctor_token["token"]
            headers = {"Authorization": f"Bearer {doctor_token}"}
            
            response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Record cannot be accessed by doctor: No data hash for blockchain verification" in response.json()["detail"]
    finally:
        # Clean up blockchain_service override
        if original_bs_override:
            app.dependency_overrides[get_blockchain_service] = original_bs_override
        else:
            del app.dependency_overrides[get_blockchain_service]





# --- POST /api/v1/medical-records/{record_id}/grant-access ---

VALID_DOCTOR_ADDRESS = "0x1234567890123456789012345678901234567890"
INVALID_DOCTOR_ADDRESS = "0xInvalidAddress"

@pytest.fixture
def created_record_for_access_tests(client: TestClient, authenticated_patient_token, db_session: Session):
    """Creates a medical record to be used for access control tests."""
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    user_did = authenticated_patient_token["user_did"] # Needed for blockchain call mock
    headers = {"Authorization": f"Bearer {token}"}

    # Mock blockchain service for record creation to ensure blockchain_record_id is set
    # This is important because the grant/revoke endpoints might implicitly assume a record
    # is on the blockchain (though our current logic relies on data_hash).
    mock_bs_for_create = AsyncMock()
    mock_bs_for_create.add_medical_record_hash.return_value = {
        "success": True, "transaction_hash": "0xcreate_record_tx_hash"
    }
    
    original_bs_override = app.dependency_overrides.get(get_blockchain_service)
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_create

    raw_data = "Test record for access control"
    # Ensure data_hash is created for this record
    data_hash_for_record = hash_data(raw_data)
    record_payload = {
        "record_type": RecordType.DIAGNOSIS.value,
        "record_metadata": {"test_type": "access_control"},
        "raw_data": raw_data
    }
    response = client.post("/api/v1/medical-records/", headers=headers, json=record_payload)
    assert response.status_code == status.HTTP_201_CREATED
    created_record_data = response.json()
    assert created_record_data["data_hash"] == data_hash_for_record # Verify hash is in response and correct
    
    # Clean up override
    if original_bs_override:
        app.dependency_overrides[get_blockchain_service] = original_bs_override
    else:
        del app.dependency_overrides[get_blockchain_service]
        
    # Return the actual data_hash from the created record, not a re-calculated one.
    return {"id": uuid.UUID(created_record_data["id"]), "data_hash": created_record_data["data_hash"], "owner_token": token, "owner_id": user_id}


def test_grant_access_success(client: TestClient, created_record_for_access_tests, db_session: Session):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    record_data_hash = created_record_for_access_tests["data_hash"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    mock_bs_for_grant = AsyncMock()
    mock_bs_for_grant.grant_record_access.return_value = {
        "success": True, "transaction_hash": "0xgrant_tx_hash"
    }
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_grant

    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/grant-access", headers=headers, json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["message"] == "Access granted successfully."
    assert response_data["record_id"] == str(record_id)
    assert response_data["doctor_address"] == VALID_DOCTOR_ADDRESS
    assert response_data["transaction_hash"] == "0xgrant_tx_hash"

    mock_bs_for_grant.grant_record_access.assert_called_once_with(
        record_hash_hex=record_data_hash,
        doctor_address=VALID_DOCTOR_ADDRESS
    )
    del app.dependency_overrides[get_blockchain_service]


def test_grant_access_record_not_found(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    non_existent_record_id = uuid.uuid4()
    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}

    response = client.post(f"/api/v1/medical-records/{non_existent_record_id}/grant-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_grant_access_not_owner(client: TestClient, created_record_for_access_tests, db_session: Session):
    record_id = created_record_for_access_tests["id"]
    
    # Create another user and token
    other_unique_suffix = uuid.uuid4().hex[:8]
    other_email = f"other_grant_test_{other_unique_suffix}@example.com"
    other_username = f"other_grant_{other_unique_suffix}"
    other_password = "otherpassword"
    
    reg_payload = {"email": other_email, "username": other_username, "password": other_password, "full_name": "Other User", "role": UserRole.PATIENT.value}
    reg_response = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == status.HTTP_201_CREATED
    
    login_data = {"username": other_username, "password": other_password}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    other_user_token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {other_user_token}"}
    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/grant-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_grant_access_invalid_doctor_address_format(client: TestClient, created_record_for_access_tests):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}
    payload = {"doctor_address": INVALID_DOCTOR_ADDRESS} # Invalid format

    response = client.post(f"/api/v1/medical-records/{record_id}/grant-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # Pydantic validation error


def test_grant_access_blockchain_service_failure_revert(client: TestClient, created_record_for_access_tests):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    record_data_hash = created_record_for_access_tests["data_hash"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    mock_bs_for_grant = AsyncMock()
    mock_bs_for_grant.grant_record_access.return_value = {
        "success": False, "error": "Smart contract execution reverted: NotRecordOwner" 
    }
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_grant

    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/grant-access", headers=headers, json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST # As per endpoint error handling
    assert "NotRecordOwner" in response.json()["detail"]
    del app.dependency_overrides[get_blockchain_service]


def test_grant_access_blockchain_service_failure_other(client: TestClient, created_record_for_access_tests):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    mock_bs_for_grant = AsyncMock()
    mock_bs_for_grant.grant_record_access.return_value = {
        "success": False, "error": "Blockchain network unavailable"
    }
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_grant

    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/grant-access", headers=headers, json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Blockchain network unavailable" in response.json()["detail"]
    del app.dependency_overrides[get_blockchain_service]

# --- END POST /api/v1/medical-records/{record_id}/grant-access ---


# --- POST /api/v1/medical-records/{record_id}/revoke-access ---

def test_revoke_access_success(client: TestClient, created_record_for_access_tests, db_session: Session):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    record_data_hash = created_record_for_access_tests["data_hash"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    mock_bs_for_revoke = AsyncMock()
    mock_bs_for_revoke.revoke_record_access.return_value = {
        "success": True, "transaction_hash": "0xrevoke_tx_hash"
    }
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_revoke

    payload = {"doctor_address": VALID_DOCTOR_ADDRESS} # Address being revoked
    response = client.post(f"/api/v1/medical-records/{record_id}/revoke-access", headers=headers, json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["message"] == "Access revoked successfully."
    assert response_data["record_id"] == str(record_id)
    assert response_data["doctor_address"] == VALID_DOCTOR_ADDRESS
    assert response_data["transaction_hash"] == "0xrevoke_tx_hash"

    mock_bs_for_revoke.revoke_record_access.assert_called_once_with(
        record_hash_hex=record_data_hash,
        doctor_address=VALID_DOCTOR_ADDRESS
    )
    del app.dependency_overrides[get_blockchain_service]


def test_revoke_access_record_not_found(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    non_existent_record_id = uuid.uuid4()
    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}

    response = client.post(f"/api/v1/medical-records/{non_existent_record_id}/revoke-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_revoke_access_not_owner(client: TestClient, created_record_for_access_tests, db_session: Session):
    record_id = created_record_for_access_tests["id"]
    
    # Create another user and token (similar to grant_access_not_owner)
    other_unique_suffix = uuid.uuid4().hex[:8]
    other_email = f"other_revoke_test_{other_unique_suffix}@example.com"
    other_username = f"other_revoke_{other_unique_suffix}"
    # ... (rest of other user creation and login) ...
    reg_payload = {"email": other_email, "username": other_username, "password": "otherpassword", "full_name": "Other User Revoke", "role": UserRole.PATIENT.value}
    reg_response = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == status.HTTP_201_CREATED
    login_data = {"username": other_username, "password": "otherpassword"}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    other_user_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {other_user_token}"}
    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/revoke-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_revoke_access_invalid_doctor_address_format(client: TestClient, created_record_for_access_tests):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}
    payload = {"doctor_address": INVALID_DOCTOR_ADDRESS}

    response = client.post(f"/api/v1/medical-records/{record_id}/revoke-access", headers=headers, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_revoke_access_blockchain_service_failure_revert(client: TestClient, created_record_for_access_tests):
    record_id = created_record_for_access_tests["id"]
    owner_token = created_record_for_access_tests["owner_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    mock_bs_for_revoke = AsyncMock()
    mock_bs_for_revoke.revoke_record_access.return_value = {
        "success": False, "error": "Smart contract execution reverted: NotRecordOwner"
    }
    app.dependency_overrides[get_blockchain_service] = lambda: mock_bs_for_revoke

    payload = {"doctor_address": VALID_DOCTOR_ADDRESS}
    response = client.post(f"/api/v1/medical-records/{record_id}/revoke-access", headers=headers, json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "NotRecordOwner" in response.json()["detail"]
    del app.dependency_overrides[get_blockchain_service]

# --- END POST /api/v1/medical-records/{record_id}/revoke-access ---
