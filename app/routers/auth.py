from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse, UserInfo
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.utils.auth import create_access_token, create_refresh_token
from app.dependencies import get_current_user
from app.models.auth import TokenData
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    user_service = UserService()
    token_service = TokenService()
    
    # Authenticate user
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "roles": user.roles}
    )
    refresh_token = create_refresh_token()
    
    # Store refresh token
    await token_service.create_refresh_token(str(user.id), refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    user_service = UserService()
    token_service = TokenService()
    
    # Create user
    user_data = {
        "email": register_data.email,
        "password": register_data.password,
        "name": register_data.name,
        "roles": ["user"]
    }
    user = await user_service.create_user(user_data)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "roles": user.roles}
    )
    refresh_token = create_refresh_token()
    
    # Store refresh token
    await token_service.create_refresh_token(str(user.id), refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    user_service = UserService()
    user = await user_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserInfo(
        id=str(user.id),
        email=user.email,
        name=user.name,
        roles=user.roles
    )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    token_service = TokenService()
    
    # Delete all refresh tokens for the user
    await token_service.delete_user_tokens(current_user.user_id)
    
    return {"message": "Successfully logged out"} 