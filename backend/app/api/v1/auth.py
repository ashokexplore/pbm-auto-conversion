"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    PasswordReset,
    PasswordUpdate,
    UserResponse
)
from app.core.supabase import supabase
from app.core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        
    Returns:
        TokenResponse: Access token and user data
    """
    try:
        # Register user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        return TokenResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            expires_in=response.session.expires_in,
            refresh_token=response.session.refresh_token,
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                created_at=response.user.created_at,
                user_metadata=response.user.user_metadata
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password
    
    Args:
        credentials: User login credentials
        
    Returns:
        TokenResponse: Access token and user data
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return TokenResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            expires_in=response.session.expires_in,
            refresh_token=response.session.refresh_token,
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                created_at=response.user.created_at,
                user_metadata=response.user.user_metadata
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    
    Args:
        current_user: Current authenticated user
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User data
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        created_at=current_user["created_at"],
        user_metadata=current_user.get("user_metadata")
    )


@router.post("/password-reset")
async def request_password_reset(data: PasswordReset):
    """
    Request password reset email
    
    Args:
        data: Password reset request data
    """
    try:
        supabase.auth.reset_password_email(data.email)
        return {"message": "Password reset email sent"}
    
    except Exception as e:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link will be sent"}


@router.post("/password-update")
async def update_password(
    data: PasswordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user password
    
    Args:
        data: New password data
        current_user: Current authenticated user
    """
    try:
        supabase.auth.update_user({
            "password": data.password
        })
        return {"message": "Password updated successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password update failed: {str(e)}"
        )

