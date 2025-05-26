import uuid
import pytest
from sqlalchemy.orm import Session

from src.app.crud import crud_user, crud_medical_record
from src.app.models.user import UserCreate, UserRole
from src.app.models.medical_record import MedicalRecordCreate, RecordType
from src.app.core.encryption import encrypt_data, hash_data, generate_encryption_key

# Helper to create a test user directly for CRUD tests
def create_test_user(db: Session, user_id: uuid.UUID = None) -> crud_user.User:
    if user_id is None:
        user_id = uuid.uuid4()
    
    # Generate a unique email and username for each test user
    unique_email = f"testuser_{user_id}@example.com"
    unique_username = f"testuser_{user_id}"
    
    user_in = UserCreate(
        email=unique_email,
        username=unique_username, # Added username
        password="testpassword123",
        full_name="Test User",
        did=f"did:example:{user_id}", # Assign a unique DID
        role=UserRole.PATIENT
    )
    # Use the actual CRUD function to create the user
    # This ensures consistency with how users are created in the app
    # Note: crud_user.create_user might have dependencies (like blockchain)
    # For isolated CRUD testing, one might directly create User ORM object,
    # but using the CRUD function is a more integrated test of the CRUD layer itself.
    # For simplicity here, assuming direct ORM object creation or a simplified user creation.
    
    # Simplified user creation for CRUD test focus:
    # Generate DID directly as it's not part of UserCreate Pydantic model
    generated_did = f"did:example:crud_test:{user_id}"

    db_user = crud_user.User( # crud_user.User is the ORM model
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        hashed_password=crud_user.get_password_hash(user_in.password), 
        full_name=user_in.full_name,
        did=generated_did, # Assign the generated DID
        role=UserRole(user_in.role), # Convert string role from Pydantic to UserRole enum for ORM
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@pytest.fixture
def test_patient(db_session: Session) -> crud_user.User:
    return create_test_user(db_session)

# Generate a fixed encryption key for consistent testing of encrypted data
# In real scenarios, keys should be managed securely, not hardcoded or fixed.
TEST_ENCRYPTION_KEY = generate_encryption_key()


def test_create_medical_record(db_session: Session, test_patient: crud_user.User):
    """
    Test creating a medical record.
    """
    raw_data_content = "Patient has a slight fever. Temperature: 37.5 C"
    encrypted_blob = encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY)
    data_h = hash_data(raw_data_content)

    record_in = MedicalRecordCreate(
        record_type=RecordType.DIAGNOSIS,
        record_metadata={"doctor_id": "doc_123", "hospital": "General Hospital"}, # Changed metadata to record_metadata
        raw_data=raw_data_content 
    )

    db_record = crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=record_in,
        patient_id=test_patient.id,
        encrypted_data=encrypted_blob,
        data_hash=data_h
    )

    assert db_record is not None
    assert db_record.id is not None
    assert db_record.patient_id == test_patient.id
    assert db_record.record_type == RecordType.DIAGNOSIS
    # Check that 'metadata' from Pydantic model is stored as 'record_metadata' in DB
    assert db_record.record_metadata == {"doctor_id": "doc_123", "hospital": "General Hospital"}
    assert db_record.encrypted_data == encrypted_blob
    assert db_record.data_hash == data_h
    assert db_record.blockchain_record_id is None # Initially None


def test_get_medical_record_by_id(db_session: Session, test_patient: crud_user.User):
    """
    Test retrieving a medical record by its ID.
    """
    raw_data_content = "Lab result: Blood sugar normal."
    encrypted_blob = encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY)
    data_h = hash_data(raw_data_content)
    record_in = MedicalRecordCreate(record_type=RecordType.LAB_RESULT, raw_data=raw_data_content)

    created_record = crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=record_in,
        patient_id=test_patient.id,
        encrypted_data=encrypted_blob,
        data_hash=data_h
    )

    fetched_record = crud_medical_record.get_medical_record_by_id(db_session, record_id=created_record.id)
    assert fetched_record is not None
    assert fetched_record.id == created_record.id
    assert fetched_record.data_hash == data_h

    # Test with non-existent ID
    non_existent_id = uuid.uuid4()
    fetched_record_none = crud_medical_record.get_medical_record_by_id(db_session, record_id=non_existent_id)
    assert fetched_record_none is None


def test_get_medical_records_by_patient_id(db_session: Session, test_patient: crud_user.User):
    """
    Test retrieving records for a specific patient, including pagination.
    """
    # Create a couple of records for the test_patient
    raw_data1 = "Record 1 data"
    crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.PRESCRIPTION, raw_data=raw_data1),
        patient_id=test_patient.id,
        encrypted_data=encrypt_data(raw_data1, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(raw_data1)
    )
    raw_data2 = "Record 2 data"
    crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.TREATMENT_PLAN, raw_data=raw_data2),
        patient_id=test_patient.id,
        encrypted_data=encrypt_data(raw_data2, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(raw_data2)
    )

    # Create another patient and a record for them, to ensure we only get records for test_patient
    other_patient = create_test_user(db_session, user_id=uuid.uuid4())
    raw_data_other = "Other patient record"
    crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=MedicalRecordCreate(record_type=RecordType.DIAGNOSIS, raw_data=raw_data_other),
        patient_id=other_patient.id,
        encrypted_data=encrypt_data(raw_data_other, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(raw_data_other)
    )
    
    # Test fetching all records for test_patient
    all_records = crud_medical_record.get_medical_records_by_patient_id(db_session, patient_id=test_patient.id)
    assert len(all_records) == 2
    for record in all_records:
        assert record.patient_id == test_patient.id

    # Test pagination: limit
    limited_records = crud_medical_record.get_medical_records_by_patient_id(
        db_session, patient_id=test_patient.id, limit=1
    )
    assert len(limited_records) == 1

    # Test pagination: skip
    skipped_records = crud_medical_record.get_medical_records_by_patient_id(
        db_session, patient_id=test_patient.id, skip=1, limit=1
    )
    assert len(skipped_records) == 1
    assert skipped_records[0].id != limited_records[0].id # Ensure skip actually skips

    # Test with a patient who has no records
    patient_with_no_records = create_test_user(db_session, user_id=uuid.uuid4())
    no_records = crud_medical_record.get_medical_records_by_patient_id(
        db_session, patient_id=patient_with_no_records.id
    )
    assert len(no_records) == 0


def test_update_medical_record_blockchain_id(db_session: Session, test_patient: crud_user.User):
    """
    Test updating the blockchain_record_id of a medical record.
    """
    raw_data_content = "Record to be updated with blockchain ID."
    record_in = MedicalRecordCreate(record_type=RecordType.VITAL_SIGNS, raw_data=raw_data_content)
    created_record = crud_medical_record.create_medical_record(
        db=db_session,
        medical_record_in=record_in,
        patient_id=test_patient.id,
        encrypted_data=encrypt_data(raw_data_content, TEST_ENCRYPTION_KEY),
        data_hash=hash_data(raw_data_content)
    )
    assert created_record.blockchain_record_id is None

    new_blockchain_id = "0x123abc456def789ghi"
    updated_record = crud_medical_record.update_medical_record_blockchain_id(
        db=db_session, record_id=created_record.id, blockchain_tx_hash=new_blockchain_id
    )
    assert updated_record is not None
    assert updated_record.id == created_record.id
    assert updated_record.blockchain_record_id == new_blockchain_id

    # Test updating a non-existent record
    non_existent_id = uuid.uuid4()
    updated_none = crud_medical_record.update_medical_record_blockchain_id(
        db=db_session, record_id=non_existent_id, blockchain_tx_hash="0xwhatever"
    )
    assert updated_none is None
