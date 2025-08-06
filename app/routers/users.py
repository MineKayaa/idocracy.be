from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.dependencies import require_admin, get_current_user
from app.models.auth import TokenData

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: TokenData = Depends(require_admin)):
    """List all users (admin only)"""
    user_service = UserService()
    return await user_service.get_all_users()


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, current_user: TokenData = Depends(require_admin)):
    """Add new user (admin only)"""
    user_service = UserService()
    return await user_service.create_user(user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get user by ID (admin or self)"""
    user_service = UserService()
    
    # Check if user is admin or requesting their own data
    if "admin" not in current_user.roles and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user_data: UserUpdate, 
    current_user: TokenData = Depends(get_current_user)
):
    """Update user (admin or self)"""
    user_service = UserService()
    
    # Check if user is admin or updating their own data
    if "admin" not in current_user.roles and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's data"
        )
    
    # Non-admin users can't update roles
    if "admin" not in current_user.roles and user_data.roles is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update roles"
        )
    
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: TokenData = Depends(require_admin)):
    """Remove user (admin only)"""
    user_service = UserService()
    
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"} 