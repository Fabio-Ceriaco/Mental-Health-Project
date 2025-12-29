from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """Base schema for user data."""

    email: EmailStr = Field(..., description="User's email address")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(..., description="User's email address")
    employee_id: int | None = Field(
        None, description="Associated employee ID", exclude=True
    )
    password: str = Field(..., min_length=8, description="User's password")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(None, description="User's email address")
    is_active: Optional[bool] = Field(
        None, description="Indicates if the user is active"
    )

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: int = Field(..., description="ID of the user")
    employee_id: int = Field(..., description="Associated employee ID")
    email: EmailStr = Field(..., description="User's email address")
    role: str = Field(..., description="Role of the ")

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):

    id: int = Field(..., description="ID of the user")
    email: EmailStr = Field(..., description="User's email address")


class ResetPasswordRequest(BaseModel):
    """Schema for requesting a password reset."""

    email: EmailStr = Field(..., description="User's email address")

    model_config = ConfigDict(from_attributes=True)


class ResetPasswordConfirm(BaseModel):
    """Schema for confirming a password reset."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """Schema for changing the password."""

    current_password: str = Field(..., min_length=8, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = ConfigDict(from_attributes=True)
