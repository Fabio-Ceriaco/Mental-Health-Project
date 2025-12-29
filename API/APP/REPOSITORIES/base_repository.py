from sqlalchemy.orm import Session
from typing import Any, List, Dict


class BaseRepository:

    def __init__(self, db_session: Session, model: Any):
        self.db_session = db_session
        self.model = model

    def create(self, obj: Any) -> Any:
        """Create a new record in the database."""

        self.db_session.add(obj)
        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    def get_all(self) -> List[Any]:
        """Retrieve all records of the model."""

        return self.db_session.query(self.model).all()

    def get_by_id(self, obj_id: int) -> Any:
        """Retrieve a record by its ID."""

        return self.db_session.query(self.model).filter(self.model.id == obj_id).first()

    def update(self, obj: Any, updates: Dict[str, Any]) -> Any:
        """Update a record with the provided fields."""

        for key, value in updates.items():
            setattr(obj, key, value)
        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    def delete(self, obj: Any) -> None:
        """Delete a record from the database."""

        self.db_session.delete(obj)
        self.db_session.commit()
