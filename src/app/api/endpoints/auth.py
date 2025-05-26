from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid

from ...core.database import get_db
from ...core.security import create_access_token, verify_password, decode_access_token
from ...core.utils import generate_did
from ...core.blockchain import blockchain_service
from ...crud import crud_user
from ...models.user import User, UserCreate, UserResponse, Token, TokenData

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Access token expiration from config (30 minutes default)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    # Check if email already exists
    db_user_by_email = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    db_user_by_username = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Generate UUID for the new user
    user_id_uuid = uuid.uuid4()
    
    # Generate DID using the UUID
    user_did = generate_did(user_id_uuid)

    # Register user on blockchain first
    blockchain_registration_result = await blockchain_service.register_user(
        user_id=user_did,
        role=user_in.role
    )

    if not blockchain_registration_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user on blockchain: {blockchain_registration_result.get('error')}",
        )
    
    # Create user in database with the generated UUID and DID
    created_user = crud_user.create_user(
        db=db, 
        user_in=user_in, 
        did=user_did,
        user_id_override=user_id_uuid
    )
    
    return created_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Try to find user by username first
    user = crud_user.get_user_by_username(db, username=form_data.username)
    # If not found by username, try email
    if not user:
        user = crud_user.get_user_by_email(db, email=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
async def login_for_access_token_json(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    # Try to find user by username first
    user = crud_user.get_user_by_username(db, username=user_credentials.username_or_email)
    # If not found by username, try email
    if not user:
        user = crud_user.get_user_by_email(db, email=user_credentials.username_or_email)

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user 