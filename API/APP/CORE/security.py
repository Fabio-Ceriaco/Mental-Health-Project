# System
import os
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from APP.DATABASE.db_conn import get_db
from enum import Enum


# Models
from APP.MODELS.user import User


class UserRole(str, Enum):
    RH = ("RH",)
    PSYCHOLOGIST = ("Psychologist",)
    ADMIN = ("Admin",)
    USER = "User"


load_dotenv()  # Load environment variables from .env file

# Load JWT configuration from environment variables
_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Ensure the secret key is set
if not _SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set")
# Set the JWT secret key
JWT_SECRET_KEY: str = _SECRET_KEY


ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""

    return pwd_context.hash(password)


def create_access_token(email: str, user_id: int):
    """Create a JWT access token."""

    # Define token payload with expiration
    payload: Dict[str, Any] = {
        "sub": email,
        "user_id": user_id,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    # Encode the JWT token
    encode_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


# Get current user from token


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    """Decode JWT token and retrieve the current user."""

    # Define exception for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT token
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")

        # Check if email is present in the token payload
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Retrieve user from the database
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.employee:
        raise credentials_exception
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    """Ensure the current user is active."""

    if not current_user.is_active:  # Check if the user is active
        raise HTTPException(
            status_code=400, detail="Inactive user"
        )  # Raise exception if inactive
    return current_user


def require_role(*roles: str):
    """Dependency to require a user to have one of the specified roles."""

    def check(user: Annotated[User, Depends(get_current_user)]):
        if user.employee.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada",
            )
        return user

    return check
