import uuid
import pytest
from unittest.mock import patch, AsyncMock

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.core.config import JWT_CONFIG # For deriving encryption key
from src.app.core.encryption import encrypt_data, decrypt_data, hash_data
from src.app.crud import crud_user, crud_medical_record
from src.app.models.user import UserCreate, UserRole
from src.app.models.medical_record import MedicalRecord, MedicalRecordCreate, RecordType, MedicalRecordDetailResponse, MedicalRecordResponse
from src.app.main import app # To ensure app context for client
from src.app.core.blockchain import get_blockchain_service # Import for overriding

# Helper to get a consistent encryption key for testing
def get_test_encryption_key() -> bytes:
    jwt_secret = JWT_CONFIG.get("secret_key", "test-secret-key-for-jwt")
    if len(jwt_secret) >= 32:
        return jwt_secret[:32].encode('utf-8')
    else:
        return (jwt_secret + '0'*(32-len(jwt_secret))).encode('utf-8')

TEST_ENCRYPTION_KEY = get_test_encryption_key()

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
        "user_did": user_did_from_me # This should be the DID string
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

def test_get_my_medical_records(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create some records for this user
    raw1 = "My record 1"
    crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.PRESCRIPTION, raw_data=raw1, record_metadata={}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw1, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw1)
    )
    raw2 = "My record 2"
    crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.VACCINATION, raw_data=raw2, record_metadata={}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw2, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw2)
    )

    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records = response.json()
    assert len(records) == 2
    assert all(r["patient_id"] == str(user_id) for r in records)
    assert "raw_data" not in records[0] # MedicalRecordResponse should not have raw_data

def test_get_my_medical_records_no_records(client: TestClient, authenticated_patient_token):
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/medical-records/patient/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    records = response.json()
    assert len(records) == 0


# --- GET /api/v1/medical-records/{record_id} ---

def test_get_medical_record_detail_success(client: TestClient, authenticated_patient_token, db_session: Session):
    token = authenticated_patient_token["token"]
    user_id = authenticated_patient_token["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    raw_data_content = "Detailed vital signs: BP 120/80, HR 70."
    created_db_record = crud_medical_record.create_medical_record(
        db_session, 
        medical_record_in=MedicalRecordCreate(record_type=RecordType.VITAL_SIGNS, raw_data=raw_data_content, record_metadata={"device":"Oximeter"}),
        patient_id=user_id, 
        encrypted_data=encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY), 
        data_hash=hash_data(raw_data_content)
    )
    record_id = created_db_record.id

    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    record_detail = response.json()
    # Manually validate against the Pydantic model if necessary, or trust FastAPI's response_model
    validated_detail = MedicalRecordDetailResponse.model_validate(record_detail)

    assert validated_detail.id == record_id
    assert validated_detail.patient_id == user_id
    assert validated_detail.record_type == RecordType.VITAL_SIGNS
    assert validated_detail.record_metadata == {"device":"Oximeter"}
    assert validated_detail.raw_data == raw_data_content # Decrypted data should be present

    # Verify in DB (ensure the original ORM model still uses record_metadata)
    db_record = crud_medical_record.get_medical_record_by_id(db_session, record_id=created_db_record.id)
    assert db_record is not None
    assert db_record.patient_id == user_id
    assert db_record.record_metadata == {"device":"Oximeter"}
    assert db_record.data_hash == hash_data(raw_data_content)
    assert db_record.blockchain_record_id == created_db_record.blockchain_record_id
    
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
    
    # Try to access it with authenticated_patient_token
    token = authenticated_patient_token["token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/medical-records/{other_record.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

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
    created_db_record = crud_medical_record.create_medical_record(
        db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.LAB_RESULT, raw_data=raw_data_content, record_metadata={"sample_id": "S123"}),
        patient_id=user_id,
        encrypted_data=encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(raw_data_content)
    )
    record_id = created_db_record.id

    response = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to decrypt record data" in response.json()["detail"]
    mock_decrypt_data.assert_called_once_with(created_db_record.encrypted_data, TEST_ENCRYPTION_KEY)
