from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from app.models.app_user import AppUserCreate
from app.models.user import UserResponse
from app.services.app_user_service import AppUserService
from app.services.app_service import AppService
from app.dependencies import get_current_user
from app.models.auth import TokenData


class AddUserToAppRequest(BaseModel):
    user_id: str
    roles: List[str] = ["viewer"]

router = APIRouter(prefix="/apps", tags=["App Users"])


@router.post("/{app_id}/users")
async def add_user_to_app(
    app_id: str,
    user_data: AddUserToAppRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Add user to app"""
    app_user_service = AppUserService()
    app_service = AppService()
    
    # Check if app exists
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if user is admin or app creator
    if "admin" not in current_user.roles and app.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage users for this app"
        )
    
    # Create app_user data
    app_user_data = AppUserCreate(
        user_id=user_data.user_id,
        app_id=app_id,
        roles=user_data.roles
    )
    
    try:
        result = await app_user_service.add_user_to_app(app_user_data)
        return {"message": "User added to app successfully", "app_user": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID or other error"
        )


@router.get("/{app_id}/users", response_model=List[UserResponse])
async def get_app_users(app_id: str, current_user: TokenData = Depends(get_current_user)):
    """List app users"""
    app_user_service = AppUserService()
    app_service = AppService()
    
    # Check if app exists
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if user is admin, app creator, or app member
    if "admin" not in current_user.roles and app.created_by != current_user.user_id:
        # Check if user is a member of the app
        user_apps = await app_user_service.get_user_apps(current_user.user_id)
        if app_id not in user_apps:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view users for this app"
            )
    
    return await app_user_service.get_app_users(app_id)


@router.delete("/{app_id}/users/{user_id}")
async def remove_user_from_app(
    app_id: str,
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Remove user from app"""
    app_user_service = AppUserService()
    app_service = AppService()
    
    # Check if app exists
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if user is admin or app creator
    if "admin" not in current_user.roles and app.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove users from this app"
        )
    
    success = await app_user_service.remove_user_from_app(app_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in app"
        )
    
    return {"message": "User removed from app successfully"} 