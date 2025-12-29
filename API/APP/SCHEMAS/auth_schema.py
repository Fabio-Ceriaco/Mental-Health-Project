from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from APP.SCHEMAS.employee_schema import EmployeeBase
from APP.SCHEMAS.user_schema import UserBase


class TokenDataSchema(BaseModel):
    """Schema para dados do token de autenticação."""

    access_token: str
    token_type: str = "bearer"
    user: Optional[UserBase] = None
    employee: Optional[EmployeeBase] = None

    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)
