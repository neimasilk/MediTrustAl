import uuid
from typing import List
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.core.config import API_V1_STR
from src.app.models.user import User, UserCreate # Corrected import for UserCreate
from src.app.models.audit_log import AuditDataAccessLog
from src.app.crud.crud_user import create_user
from src.app.crud.crud_audit_log import create_audit_log as crud_create_audit_log # Renamed to avoid conflict
from src.app.schemas.audit_log import AuditLogResponse

# Fixture for creating a test user and authenticating is assumed to be in conftest.py
# or would need to be created here. For this example, we'll assume client and test_db fixtures exist.
# We'll also assume a way to get an authenticated client or token.

def get_user_token_headers(client: TestClient, username: str, password: str) -> dict:
    # OAuth2PasswordRequestForm expects 'username' and 'password' fields
    # The endpoint /api/v1/auth/login uses OAuth2PasswordRequestForm
    form_data = {
        "username": username, # 'username' field can be username or email as handled by endpoint
        "password": password,
    }
    r = client.post(f"{API_V1_STR}/auth/login", data=form_data)
    r.raise_for_status() # Ensure login was successful
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

@pytest.fixture(scope="function") # Changed scope to function
def test_user_for_audit(db_session: Session) -> User:
    user_in = UserCreate(
        email="auditowner@example.com",
        username="auditowner",
        password="testpassword",
        full_name="Audit Owner User",
        role="PATIENT" # Role as string, User model will handle enum conversion
    )
    # Provide a dummy DID for the test user
    user_did = f"did:example:{user_in.username}"
    user = create_user(db=db_session, user_in=user_in, did=user_did)
    return user

@pytest.fixture(scope="function") # Changed scope to function
def test_actor_user_for_audit(db_session: Session) -> User:
    user_in = UserCreate(
        email="auditactor@example.com",
        username="auditactor",
        password="testpassword",
        full_name="Audit Actor User",
        role="DOCTOR"
    )
    # Provide a dummy DID for the test user
    actor_did = f"did:example:{user_in.username}"
    user = create_user(db=db_session, user_in=user_in, did=actor_did)
    return user


def test_get_my_record_access_history(
    client: TestClient, db_session: Session, test_user_for_audit: User, test_actor_user_for_audit: User # Changed db to db_session
):
    # Get auth token for test_user_for_audit
    headers = get_user_token_headers(client, "auditowner", "testpassword")

    # Create some audit logs
    # Log 1: test_user_for_audit is owner, test_actor_user_for_audit is actor
    log1 = crud_create_audit_log(
        db_session, # Changed db to db_session
        actor_user_id=test_actor_user_for_audit.id,
        owner_user_id=test_user_for_audit.id,
        action_type="VIEW_RECORD_SUCCESS",
        ip_address="192.168.1.1",
    )
    # Simulate time difference for ordering
    # This is a bit hacky for tests; ideally, use a time library or pass datetime to CRUD
    log1.timestamp = datetime.utcnow() - timedelta(minutes=10)
    db_session.commit() # Changed db to db_session


    # Log 2: test_user_for_audit is owner, test_actor_user_for_audit is actor (newer)
    log2 = crud_create_audit_log(
        db_session, # Changed db to db_session
        actor_user_id=test_actor_user_for_audit.id,
        owner_user_id=test_user_for_audit.id,
        action_type="GRANT_ACCESS_SUCCESS",
        target_address="0xDoctorAddress",
        ip_address="192.168.1.2",
    )
    log2.timestamp = datetime.utcnow() - timedelta(minutes=5)
    db_session.commit() # Changed db to db_session

    # Log 3: test_user_for_audit is actor, test_actor_user_for_audit is owner (should not appear)
    crud_create_audit_log(
        db_session, # Changed db to db_session
        actor_user_id=test_user_for_audit.id,
        owner_user_id=test_actor_user_for_audit.id,
        action_type="VIEW_RECORD_SUCCESS",
        ip_address="192.168.1.3",
    )

    # Log 4: Another user (test_actor_user_for_audit) is owner (should not appear)
    another_actor_id = uuid.uuid4() # Dummy ID for this
    db_session.add(User(id=another_actor_id, username="anotheractor", email="anotheractor@example.com", hashed_password="pwd", role="DOCTOR", did="did:another", full_name="Another Actor")) # Changed db to db_session
    db_session.commit() # Changed db to db_session
    crud_create_audit_log(
        db_session, # Changed db to db_session
        actor_user_id=another_actor_id,
        owner_user_id=test_actor_user_for_audit.id,
        action_type="LOGIN_SUCCESS",
        ip_address="192.168.1.4",
    )
    
    # Call the endpoint
    response = client.get(f"{API_V1_STR}/audit/my-record-access-history", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    # Verify order (newest first based on manual timestamp adjustment)
    assert data[0]["id"] == str(log2.id)
    assert data[0]["action_type"] == "GRANT_ACCESS_SUCCESS"
    assert data[0]["owner_user_id"] == str(test_user_for_audit.id)
    assert data[0]["actor_user_id"] == str(test_actor_user_for_audit.id)
    assert data[0]["target_address"] == "0xDoctorAddress"

    assert data[1]["id"] == str(log1.id)
    assert data[1]["action_type"] == "VIEW_RECORD_SUCCESS"
    assert data[1]["owner_user_id"] == str(test_user_for_audit.id)
    assert data[1]["actor_user_id"] == str(test_actor_user_for_audit.id)

    # Test pagination
    response_limit1 = client.get(f"{API_V1_STR}/audit/my-record-access-history?limit=1", headers=headers)
    assert response_limit1.status_code == 200
    data_limit1 = response_limit1.json()
    assert len(data_limit1) == 1
    assert data_limit1[0]["id"] == str(log2.id)

    response_skip1_limit1 = client.get(f"{API_V1_STR}/audit/my-record-access-history?skip=1&limit=1", headers=headers)
    assert response_skip1_limit1.status_code == 200
    data_skip1_limit1 = response_skip1_limit1.json()
    assert len(data_skip1_limit1) == 1
    assert data_skip1_limit1[0]["id"] == str(log1.id)

    # Test with a user who has no owned logs (test_actor_user_for_audit logs where they are owner)
    actor_headers = get_user_token_headers(client, "auditactor", "testpassword")
    response_actor = client.get(f"{API_V1_STR}/audit/my-record-access-history", headers=actor_headers)
    assert response_actor.status_code == 200
    data_actor = response_actor.json()
    # We created two logs where test_actor_user_for_audit was owner (Log 3 and Log 4)
    assert len(data_actor) == 2
    # Order will depend on timestamps, which are not manually set for Log 3 and Log 4.
    # We just need to ensure both logs for this owner are present.
    owner_ids_in_response = {log["owner_user_id"] for log in data_actor}
    actor_ids_in_log3_response = {log["actor_user_id"] for log in data_actor if log["action_type"] == "VIEW_RECORD_SUCCESS"}
    actor_ids_in_log4_response = {log["actor_user_id"] for log in data_actor if log["action_type"] == "LOGIN_SUCCESS"}

    assert all(owner_id == str(test_actor_user_for_audit.id) for owner_id in owner_ids_in_response)
    assert str(test_user_for_audit.id) in actor_ids_in_log3_response
    # The actor for Log 4 (another_actor_id) is not explicitly checked here beyond ensuring the log is present.
    # The key is that both logs for test_actor_user_for_audit as owner are returned.
