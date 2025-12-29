# System
from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from typing import Dict

# Models
from APP.CORE.security import get_password_hash
from APP.MODELS.user import User

# Repositories
from APP.REPOSITORIES.user_repository import UsersRepository

# Schemas
from APP.SCHEMAS.user_schema import UserUpdate


class UserService:

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.repo = UsersRepository(db_session)

    """Service for managing User operations."""

    def create_user(
        self, email: str, password: str, employee_id: int
    ) -> Dict[str, str | User]:
        """Create a new user after checking for email uniqueness."""
        
        password_regex = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )

        if not password_regex.match(password):
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long, include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character.",
            )
        hashed_password = get_password_hash(password)
        
        user = User(
            email=email,
            password=hashed_password,
            employee_id=employee_id,
            is_active=True,
        )
        self.repo.new_user(user)
        return user

    def get_user(self, user_id: int):
        """Retrieve a user by their ID."""

        return self.repo.get_by_id(user_id)

    def get_user_by_email(self, email: str):
        """Retrieve a user by their email."""

        return self.repo.get_user_by_email(email)

    def has_user_for_employee(self, employee_id: int) -> bool:
        """Check if there is a user associated with the given employee ID."""

        user = (
            self.db_session.query(User).filter(User.employee_id == employee_id).first()
        )
        return user is not None

    def get_all_users(self):
        """Retrieve all users."""

        return self.repo.get_all()

    def update_user(self, user_id: int, user: UserUpdate):
        """Update an existing user's details."""

        db_user = self.repo.get_by_id(user_id)
        if not db_user:
            raise ValueError("User not found.")
        update_data = user.model_dump(exclude_unset=True)
        return self.repo.update(db_user, update_data)

    def delete_user(self, user_id: int):
        """Delete a user by their ID."""

        db_user = self.repo.get_by_id(user_id)
        if not db_user:
            raise ValueError("User not found.")
        return self.repo.delete(db_user)
