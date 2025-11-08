"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    created_at: str
    user_metadata: Optional[dict] = None


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user: UserResponse


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordUpdate(BaseModel):
    """Password update schema"""
    password: str = Field(..., min_length=8, description="New password must be at least 8 characters")

