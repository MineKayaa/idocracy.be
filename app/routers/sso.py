from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from typing import List
from app.models.app import AppResponse
from app.models.user import UserResponse
from app.services.app_service import AppService
from app.services.app_user_service import AppUserService
from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.models.auth import TokenData
from app.utils.auth import create_access_token
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/sso", tags=["SSO"])


@router.get("/dashboard", response_model=List[AppResponse])
async def get_user_dashboard(current_user: TokenData = Depends(get_current_user)):
    """Get all apps that the user has access to"""
    app_user_service = AppUserService()
    app_service = AppService()
    
    # Get all app IDs that the user belongs to
    user_app_ids = await app_user_service.get_user_apps(current_user.user_id)
    
    # Get app details for each app
    user_apps = []
    for app_id in user_app_ids:
        app = await app_service.get_app_by_id(app_id)
        if app:
            user_apps.append(app)
    
    return user_apps


@router.get("/launch/{app_id}")
async def launch_app(
    app_id: str,
    current_user: TokenData = Depends(get_current_user),
    request: Request = None
):
    """Launch an app with SSO authentication"""
    app_user_service = AppUserService()
    app_service = AppService()
    
    # Check if app exists
    app = await app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if user has access to this app
    user_apps = await app_user_service.get_user_apps(current_user.user_id)
    if app_id not in user_apps:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this app"
        )
    
    # Get user details
    user_service = UserService()
    user = await user_service.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create a short-lived token for the app
    token_data = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "roles": user.roles,
        "app_id": app_id,
        "app_name": app.name
    }
    
    # Create access token with shorter expiration for SSO
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=5)  # Short-lived token for SSO
    )
    
    # Get the first redirect URI (you might want to add logic to select specific URI)
    if not app.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No redirect URIs configured for this app"
        )
    
    redirect_uri = app.redirect_uris[0]
    
    # Redirect to the app with the token
    redirect_url = f"{redirect_uri}?token={access_token}&user_id={user.id}&email={user.email}"
    
    # For testing, return the redirect URL instead of redirecting
    #    return RedirectResponse(url=redirect_url, status_code=302)
    return {
        "redirect_url": redirect_url,
        "token": access_token,
        "user_id": user.id,
        "email": user.email,
        "app_name": app.name
    }


@router.post("/verify")
async def verify_sso_token(token: str):
    """Verify SSO token (for client apps to verify authentication)"""
    from app.utils.auth import verify_token
    
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "user_id": token_data.user_id,
        "email": token_data.email,
        "roles": token_data.roles
    } 