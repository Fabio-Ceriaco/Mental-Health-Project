# System
from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from APP.CORE.security import get_password_hash

# Models
from APP.MODELS import User

# Schemas
from APP.SCHEMAS.user_schema import UserUpdate

# Repositories
from APP.REPOSITORIES.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    """Repository for managing User in the database."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, User)

    def get_by_id(self, obj_id: int) -> User:
        """Retrieve a user by their ID."""

        return self.db_session.query(User).filter(User.id == obj_id).first()

    def get_user_by_email(self, email: str) -> User:
        """Retrieve a user by their email."""

        return self.db_session.query(User).filter(User.email == email).first()

    def get_all(self) -> list[User]:
        """Retrieve all users."""

        return self.db_session.query(User).all()

    def new_user(self, user: User):
        """Create a new user in the database."""
        try:
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
        except IntegrityError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao criar utilizador: {str(e)}",
            )

    def update_user(self, db_user: User, updates: UserUpdate) -> User:
        """Update an existing user in the database."""

        # Apply updates to the user
        for key, value in updates.model_dump(
            exclude_unset=True
        ).items():  # exclude_unset to avoid overwriting with None
            if key == "password":  # hash the password if it's being updated
                value = get_password_hash(value)  # hash the new password
            setattr(db_user, key, value)  # set the updated value

        self.db_session.commit()
        self.db_session.refresh(db_user)
        return db_user

    def delete_user(self, db_user: User) -> User | None:
        """Delete a user from the database."""

        db_user = self.db_session.query(User).filter(User.id == db_user.id).first()

        if not db_user:
            return None

        self.db_session.delete(db_user)
        self.db_session.commit()
        return db_user
