import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from src.app.models.audit_log import AuditDataAccessLog
from src.app.models.user import User
from src.app.models.medical_record import MedicalRecord, RecordType
from src.app.crud.crud_audit_log import create_audit_log
from src.app.crud import crud_audit_log # Added import for the module itself
from src.app.core.database import Base

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)  # Create tables
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine) # Drop tables after test

def test_create_audit_log(db: Session):
    # Create dummy users and medical record for FK constraints
    # These would normally be created using their own CRUD functions or fixtures
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    record_id = uuid.uuid4()

    # Manually add them to the session for the test since we don't have User/MedicalRecord CRUDs here
    # In a real scenario, use fixtures or CRUDs to create these.
    # For simplicity, we'll assume these IDs exist for the purpose of this test.
    # If User/MedicalRecord models have non-nullable fields, they'd need to be populated.
    # For now, we are testing audit log creation, so we focus on that.

    log_data = {
        "actor_user_id": user1_id,
        "owner_user_id": user2_id,
        "action_type": "VIEW_RECORD",
        "record_id": record_id,
        "ip_address": "127.0.0.1",
        "target_address": "0x1234567890abcdef1234567890abcdef12345678",
        "details": {"reason": "Routine check-up"}
    }

    # Create dummy User and MedicalRecord instances to satisfy FK constraints in SQLite
    # This is a simplified way for testing; normally, you'd use factories or more elaborate fixtures.
    # We need to add these to the session so SQLite knows about them.
    db.add(User(id=user1_id, username="actoruser", email="actor@example.com", hashed_password="hashedpassword", role="DOCTOR", blockchain_address="0xActorWallet", did=f"did:example:{user1_id}", full_name="Actor User"))
    db.add(User(id=user2_id, username="owneruser", email="owner@example.com", hashed_password="hashedpassword", role="PATIENT", blockchain_address="0xOwnerWallet", did=f"did:example:{user2_id}", full_name="Owner User"))
    db.add(MedicalRecord(
        id=record_id,
        patient_id=user2_id,
        record_type=RecordType.DIAGNOSIS, # Added required field
        encrypted_data=b"encrypted_medical_data", # Added required field
        data_hash="somehash",
        # ipfs_cid and data_key_cid are not valid fields for MedicalRecord
        # blockchain_record_id can be added if needed, it's nullable
        # record_metadata can be added if needed, it's nullable
    ))
    db.commit()


    db_log = create_audit_log(db=db, **log_data)

    assert db_log is not None
    assert db_log.id is not None
    assert db_log.timestamp is not None
    assert db_log.actor_user_id == log_data["actor_user_id"]
    assert db_log.owner_user_id == log_data["owner_user_id"]
    assert db_log.action_type == log_data["action_type"]
    assert db_log.record_id == log_data["record_id"]
    assert db_log.ip_address == log_data["ip_address"]
    assert db_log.target_address == log_data["target_address"]
    assert db_log.details == log_data["details"]

    # Verify it's in the database
    retrieved_log = db.query(AuditDataAccessLog).filter(AuditDataAccessLog.id == db_log.id).first()
    assert retrieved_log is not None
    assert retrieved_log.action_type == "VIEW_RECORD"

def test_create_audit_log_minimal(db: Session):
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    
    # Add dummy users to satisfy FK constraints
    db.add(User(id=user1_id, username="actoruser_min", email="actor_min@example.com", hashed_password="hashedpassword", role="DOCTOR", blockchain_address="0xActorWalletMin", did=f"did:example:min:{user1_id}", full_name="Actor User Min"))
    db.add(User(id=user2_id, username="owneruser_min", email="owner_min@example.com", hashed_password="hashedpassword", role="PATIENT", blockchain_address="0xOwnerWalletMin", did=f"did:example:min:{user2_id}", full_name="Owner User Min"))
    db.commit()

    log_data = {
        "actor_user_id": user1_id,
        "owner_user_id": user2_id,
        "action_type": "LOGIN_SUCCESS",
    }
    db_log = create_audit_log(db=db, **log_data)

    assert db_log is not None
    assert db_log.id is not None
    assert db_log.timestamp is not None
    assert db_log.actor_user_id == log_data["actor_user_id"]
    assert db_log.owner_user_id == log_data["owner_user_id"]
    assert db_log.action_type == log_data["action_type"]
    assert db_log.record_id is None
    assert db_log.ip_address is None
    assert db_log.target_address is None
    assert db_log.details is None

def test_get_audit_logs_by_owner(db: Session):
    # Create users
    owner1_id = uuid.uuid4()
    actor1_id = uuid.uuid4()
    owner2_id = uuid.uuid4() # Another owner for different logs

    db.add(User(id=owner1_id, username="owner1", email="owner1@example.com", hashed_password="pwd", role="PATIENT", did="did:owner1", full_name="Owner One"))
    db.add(User(id=actor1_id, username="actor1", email="actor1@example.com", hashed_password="pwd", role="DOCTOR", did="did:actor1", full_name="Actor One"))
    db.add(User(id=owner2_id, username="owner2", email="owner2@example.com", hashed_password="pwd", role="PATIENT", did="did:owner2", full_name="Owner Two"))
    db.commit()

    # Create audit logs for owner1
    # Note: AuditDataAccessLog's timestamp is auto-set by default=datetime.now(timezone.utc)
    # To control order for testing, we might need to set them manually or create them with slight delays.
    # For simplicity, we rely on creation order here and assume default timestamps will reflect that for basic ordering.
    # For more robust time-based testing, manually setting timestamps would be better.
    log1_owner1 = create_audit_log(db, actor_user_id=actor1_id, owner_user_id=owner1_id, action_type="LOGIN_SUCCESS")
    # Simulate a slight delay for timestamp differences if relying on auto-timestamps
    import time; time.sleep(0.01)
    log2_owner1 = create_audit_log(db, actor_user_id=actor1_id, owner_user_id=owner1_id, action_type="VIEW_DATA")
    import time; time.sleep(0.01)
    log3_owner1 = create_audit_log(db, actor_user_id=actor1_id, owner_user_id=owner1_id, action_type="UPDATE_DATA")

    # Create audit log for owner2
    create_audit_log(db, actor_user_id=actor1_id, owner_user_id=owner2_id, action_type="LOGIN_SUCCESS")

    # Test fetching logs for owner1
    logs_owner1 = crud_audit_log.get_audit_logs_by_owner(db, owner_user_id=owner1_id, limit=10)
    assert len(logs_owner1) == 3
    assert logs_owner1[0].id == log3_owner1.id # Newest first
    assert logs_owner1[1].id == log2_owner1.id
    assert logs_owner1[2].id == log1_owner1.id
    for log in logs_owner1:
        assert log.owner_user_id == owner1_id

    # Test pagination: skip 1, limit 1 for owner1
    logs_owner1_skip1_limit1 = crud_audit_log.get_audit_logs_by_owner(db, owner_user_id=owner1_id, skip=1, limit=1)
    assert len(logs_owner1_skip1_limit1) == 1
    assert logs_owner1_skip1_limit1[0].id == log2_owner1.id

    # Test pagination: skip 0, limit 1 for owner1
    logs_owner1_limit1 = crud_audit_log.get_audit_logs_by_owner(db, owner_user_id=owner1_id, skip=0, limit=1)
    assert len(logs_owner1_limit1) == 1
    assert logs_owner1_limit1[0].id == log3_owner1.id
    
    # Test fetching logs for owner2
    logs_owner2 = crud_audit_log.get_audit_logs_by_owner(db, owner_user_id=owner2_id, limit=10)
    assert len(logs_owner2) == 1
    assert logs_owner2[0].owner_user_id == owner2_id

    # Test fetching for a user with no logs
    non_existent_owner_id = uuid.uuid4()
    logs_non_existent = crud_audit_log.get_audit_logs_by_owner(db, owner_user_id=non_existent_owner_id)
    assert len(logs_non_existent) == 0
