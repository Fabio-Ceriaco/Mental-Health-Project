from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from APP.REPOSITORIES.user_repository import UsersRepository
from APP.CORE.security import verify_password, create_access_token
from datetime import datetime


class AuthenticationService:
    """Service for handling user authentication."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.repo = UsersRepository(db_session)

    def authenticate_user(self, email: str, password: str) -> str:
        user = self.repo.get_user_by_email(email)

        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        user.last_login = datetime.now()
        self.db.commit()

        # Create access token (no need to refresh, user object is still valid)
        access_token = create_access_token(email=user.email, user_id=user.id)

        return access_token
