from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...core.blockchain import blockchain_service

router = APIRouter()

class UserRegistration(BaseModel):
    user_id: str
    role: str

class UserResponse(BaseModel):
    user_id: str
    role: str
    is_registered: bool

@router.post("/register", response_model=dict)
async def register_user(user: UserRegistration):
    """
    Register a new user in the blockchain
    """
    result = await blockchain_service.register_user(user.user_id, user.role)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.get("/role/{user_id}", response_model=UserResponse)
async def get_user_role(user_id: str):
    """
    Get user role from the blockchain
    """
    result = await blockchain_service.get_user_role(user_id)
    if not result['success']:
        raise HTTPException(status_code=404, detail=result['error'])
    return UserResponse(
        user_id=result['user_id'],
        role=result['role'],
        is_registered=result['is_registered']
    ) 