from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.app import AppCreate, AppUpdate, AppResponse
from app.services.app_service import AppService
from app.dependencies import get_current_user
from app.models.auth import TokenData

router = APIRouter(prefix="/apps", tags=["Apps"])


@router.get("/", response_model=List[AppResponse])
async def get_apps(current_user: TokenData = Depends(get_current_user)):
    """List all apps"""
    app_service = AppService()
    return await app_service.get_all_apps()


@router.post("/", response_model=AppResponse)
async def create_app(app_data: AppCreate, current_user: TokenData = Depends(get_current_user)):
    """Register new app"""
    app_service = AppService()
    return await app_service.create_app(app_data, current_user.user_id)


@router.get("/{app_id}", response_model=AppResponse)
async def get_app(app_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get app info"""
    app_service = AppService()
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    return app


@router.put("/{app_id}", response_model=AppResponse)
async def update_app(
    app_id: str, 
    app_data: AppUpdate, 
    current_user: TokenData = Depends(get_current_user)
):
    """Update app"""
    app_service = AppService()
    
    # Check if user is admin or app creator
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    if "admin" not in current_user.roles and app.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this app"
        )
    
    updated_app = await app_service.update_app(app_id, app_data)
    if not updated_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    return updated_app


@router.delete("/{app_id}")
async def delete_app(app_id: str, current_user: TokenData = Depends(get_current_user)):
    """Delete app"""
    app_service = AppService()
    
    # Check if user is admin or app creator
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    if "admin" not in current_user.roles and app.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this app"
        )
    
    success = await app_service.delete_app(app_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    return {"message": "App deleted successfully"} 