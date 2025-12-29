from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict
from APP.MODELS import Question
from APP.REPOSITORIES.base_repository import BaseRepository


class QuestionRepository(BaseRepository):

    def __init__(self, db_session: Session):
        super().__init__(db_session, Question)

    def get_questions_by_dimension(self, dimension: str) -> List[Question]:
        """Retrieve all questions for a specific dimension."""

        return (
            self.db_session.query(self.model)
            .filter(self.model.dimension == dimension)
            .all()
        )

    def get_questions(self, limit: int = 40) -> List[Question]:
        """Retrieve a limited number of questions."""

        return (
            self.db_session.query(self.model).order_by(func.random()).limit(limit).all()
        )

    def get_question_map(self, question_ids: List[int]) -> Dict[int, Question]:
        """Retrieve questions by IDs and return a mapping of ID to Question."""

        questions = (
            self.db_session.query(self.model)
            .filter(self.model.id.in_(question_ids))
            .all()
        )
        return {q.id: q for q in questions}
