from sqlalchemy.orm import Session
import uuid
from ..models.user import User
from ..schemas.user import UserCreate, UserRole # UserCreate and UserRole are in schemas, not models
from ..core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate, did: str, user_id_override: uuid.UUID | None = None) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_in: User creation data
        did: Decentralized Identifier
        user_id_override: Optional UUID to use instead of letting PostgreSQL generate one
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        id=user_id_override if user_id_override else uuid.uuid4(), # Client-side UUID generation if not overridden
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,  # Assign full_name
        hashed_password=hashed_password,
        role=UserRole(user_in.role),  # Convert string role to enum
        did=did,
        is_active=True  # Explicitly set is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_blockchain_address(db: Session, user_id: uuid.UUID, blockchain_address: str) -> User:
    """Update a user's blockchain address."""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.blockchain_address = blockchain_address
        db.commit()
        db.refresh(db_user)
    return db_user