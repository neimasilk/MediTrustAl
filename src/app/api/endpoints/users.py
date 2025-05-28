from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel # This can be removed if not used by other local models
from sqlalchemy.orm import Session
from ...core.blockchain import get_blockchain_service
from ...core.database import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserResponse
from ..endpoints.auth import get_current_active_user

router = APIRouter()

# Removed local UserRegistration and UserResponse Pydantic models
# class UserRegistration(BaseModel):
#     user_id: str
#     role: str

# class UserResponse(BaseModel):
#     user_id: str # This was the conflicting model
#     role: str
#     is_registered: bool

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    """
    Register a new user in the blockchain
    """
    blockchain_service = get_blockchain_service()
    result = await blockchain_service.register_user(user.user_id, user.role)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current logged-in user's details.
    Requires authentication.
    """
    # The UserResponse model from schemas.user has from_attributes = True,
    # but we explicitly call model_validate to ensure correct Pydantic model construction.
    return UserResponse.model_validate(current_user)

@router.get("/{user_id}/role", response_model=dict)
async def get_user_role(user_id: str):
    """
    Get user role from the blockchain
    """
    blockchain_service = get_blockchain_service()
    result = await blockchain_service.get_user_role(user_id)
    if not result['success']:
        raise HTTPException(status_code=404, detail=result['error'])
    return {
        'user_id': result['user_id'],
        'role': result['role'],
        'is_registered': result['is_registered']
    }