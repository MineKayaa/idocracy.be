from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import TokenResponse, TokenData
from app.services.token_service import TokenService
from app.services.user_service import UserService
from app.utils.auth import create_access_token, verify_token, create_refresh_token
from app.dependencies import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/token", tags=["Token Management"])


@router.post("/verify")
async def verify_token_endpoint(token_data: dict):
    """Check if token is valid & get roles"""
    token = token_data.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    verified_data = verify_token(token)
    if not verified_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "valid": True,
        "user_id": verified_data.user_id,
        "email": verified_data.email,
        "roles": verified_data.roles
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: dict):
    """Refresh expired access token"""
    refresh_token_value = refresh_data.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    token_service = TokenService()
    user_service = UserService()
    
    # Verify refresh token exists and is not expired
    token_doc = await token_service.get_refresh_token(refresh_token_value)
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is expired
    from datetime import datetime
    if token_doc.expires_at < datetime.utcnow():
        # Clean up expired token
        await token_service.delete_refresh_token(refresh_token_value)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user data
    user = await user_service.get_user_by_id(str(token_doc.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "roles": user.roles}
    )
    
    # Create new refresh token
    new_refresh_token = create_refresh_token()
    
    # Store new refresh token and delete old one
    await token_service.create_refresh_token(str(user.id), new_refresh_token)
    await token_service.delete_refresh_token(refresh_token_value)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=30 * 60  # 30 minutes
    ) 