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
from src.app.core.blockchain import get_blockchain_service

# Mock environment variables
os.environ["GANACHE_RPC_URL"] = "http://127.0.0.1:7545"
os.environ["BLOCKCHAIN_SENDER_PRIVATE_KEY"] = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-jwt"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy import TypeDecorator, TEXT, types as sa_types
import json

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

# Custom type for SQLite to handle JSONB (stores as TEXT)
class SQLiteJSONB(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(sa_types.JSON())
        return dialect.type_descriptor(JSONB())

    def process_bind_param(self, value, dialect):
        if dialect.name == 'sqlite':
            if value is not None:
                return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'sqlite':
            if value is not None:
                return json.loads(value)
        return value

# Override JSONB for SQLite testing
from sqlalchemy.dialects import registry
registry.register("jsonb", "sqlite", SQLiteJSONB)
registry.register("postgresql.JSONB", "sqlite", SQLiteJSONB)

# Monkeypatch SQLite compiler to handle JSONB as JSON
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy import JSON as StandardJSONType

def visit_jsonb_for_sqlite(self, type_, **kw):
    # Effectively treat postgresql.JSONB as sqlalchemy.JSON for SQLite
    return self.visit_JSON(StandardJSONType(), **kw) # Changed visit_json to visit_JSON

if not hasattr(SQLiteTypeCompiler, 'visit_JSONB'):
    SQLiteTypeCompiler.visit_JSONB = visit_jsonb_for_sqlite


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    # Apply workaround for UUID and ENUM if not already handled by specific type decorators for SQLite
    from sqlalchemy.dialects.postgresql import UUID as PGUUID, ENUM as PGEnum
    from sqlalchemy import String, DateTime
    from src.app.models.medical_record import RecordType # Import your enum
    import uuid # Import uuid module

    # Removed incorrect @sa_types.TypeDecorator.cache_ok decorator
    class SQLiteUUID(sa_types.TypeDecorator):
        impl = sa_types.CHAR(36) 
        cache_ok = True # Ensure caching is enabled
        def load_dialect_impl(self, dialect):
            if dialect.name == 'sqlite':
                return dialect.type_descriptor(sa_types.CHAR(36))
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        def process_bind_param(self, value, dialect):
            if value is not None and dialect.name == 'sqlite':
                return str(value)
            return value
        def process_result_value(self, value, dialect):
            if value is not None and dialect.name == 'sqlite':
                return uuid.UUID(value)
            return value

    # Removed incorrect @sa_types.TypeDecorator.cache_ok decorator
    class SQLiteENUM(sa_types.TypeDecorator):
        impl = sa_types.String(255)
        cache_ok = True # Ensure caching is enabled
        def __init__(self, enum_class, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._enum_class = enum_class
        def load_dialect_impl(self, dialect):
            if dialect.name == 'sqlite':
                return dialect.type_descriptor(sa_types.String(50)) # Adjust length as needed
            return dialect.type_descriptor(PGEnum(self._enum_class, name=self._enum_class.__name__.lower()))
        def process_bind_param(self, value, dialect):
            if value is not None and dialect.name == 'sqlite':
                return value.value # Store enum value
            return value
        def process_result_value(self, value, dialect):
            if value is not None and dialect.name == 'sqlite':
                return self._enum_class(value)
            return value
            
    # Override PGUUID and PGEnum for SQLite testing
    registry.register("postgresql.UUID", "sqlite", SQLiteUUID)
    registry.register("UUID", "sqlite", SQLiteUUID) # Also register the generic UUID
    registry.register("postgresql.ENUM", "sqlite", SQLiteENUM) 
    # For specific enums like 'recordtype', SQLAlchemy might try to use that name.
    # We need to ensure that SQLEnum(RecordType, name="recordtype") uses our SQLiteENUM.
    # This is tricky because the name "recordtype" is specific.
    # The SQLiteENUM above is generic. If Alembic/SQLAlchemy uses a specific name for the ENUM type
    # in its internal registry for SQLite, this generic override might not be enough.
    # However, for direct model usage with SQLite, mapping PGEnum to String should work.

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
    
    # Get the service instance and mock its methods
    # This ensures we are mocking the actual instance that will be used by the app
    # and respects the lazy initialization (service is fetched only when client fixture is used)
    service_instance = get_blockchain_service()
    service_instance.register_user = mock_register_user
    service_instance.get_user_role = mock_get_user_role
    
    yield TestClient(app)
    del app.dependency_overrides[get_db] 