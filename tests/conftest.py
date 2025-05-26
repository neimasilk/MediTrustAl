import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from unittest.mock import patch

from src.app.main import app
from src.app.core.database import Base, get_db
from src.app.models.user import User
from src.app.core.blockchain import blockchain_service

# Mock environment variables
os.environ["GANACHE_RPC_URL"] = "http://127.0.0.1:7545"
os.environ["BLOCKCHAIN_SENDER_PRIVATE_KEY"] = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-jwt"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    # Mock blockchain service methods
    async def mock_register_user(user_id: str, role: str):
        return {
            'success': True,
            'transaction_hash': '0x1234567890abcdef',
            'user_id': user_id,
            'role': role
        }
    
    async def mock_get_user_role(user_id: str):
        return {
            'success': True,
            'user_id': user_id,
            'role': 'PATIENT',
            'is_registered': True
        }
    
    # Apply mocks
    app.dependency_overrides[get_db] = override_get_db
    blockchain_service.register_user = mock_register_user
    blockchain_service.get_user_role = mock_get_user_role
    
    yield TestClient(app)
    del app.dependency_overrides[get_db] 