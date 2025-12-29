# System
import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime

# Models
from APP.MODELS import EmployeeResponse, Question, AssessmentResult
from APP.MODELS.risk_level import RiskLevel

# Services
from APP.SERVICES.assessment_service import calculate_assessment, QuestionInput

# Repositories
from APP.REPOSITORIES.base_repository import BaseRepository


class AssessmentRepository(BaseRepository):

    def __init__(self, db_session: Session):
        super().__init__(db_session, AssessmentResult)

    def load_questions_by_ids(self, question_ids: List[int]) -> Dict[int, Question]:
        """Load questions from the database based on a list of questions IDs."""

        rows = (
            self.db_session.query(Question).filter(Question.id.in_(question_ids)).all()
        )
        return {row.id: row for row in rows}

    def save_employee_responses(
        self, employee_id: int, assessment_id: int, responses: List[Dict[str, Any]]
    ) -> List[EmployeeResponse]:
        """Saves employee responses to the database."""

        objs: List[EmployeeResponse] = []

        for resp in responses:
            emp_resp = EmployeeResponse(
                employee_id=employee_id,
                assessment_id=assessment_id,
                question_id=resp["question_id"],
                answer_value=resp["answer_value"],
            )
            self.db_session.add(emp_resp)
            objs.append(emp_resp)
        self.db_session.commit()
        return objs

    def _get_risk_level_id(self, risk_label: str) -> int:
        """Maps risk label to risk level ID."""

        risk = (
            self.db_session.query(RiskLevel)
            .filter(RiskLevel.name == risk_label)
            .first()
        )

        if not risk:
            raise ValueError(f'Risk level "{risk_label}" not found in database.')
        return risk.id

    def save_assessment_result(
        self, employee_id: int, assessment_id: int, result_data: Dict[str, Any]
    ) -> AssessmentResult:
        """Saves the assessment result to the database."""

        ar = AssessmentResult(
            employee_id=employee_id,
            score_total=result_data["score_total"],
            score_percent=result_data["score_percent"],
            risk_level_id=result_data["risk_level"],
            details_json=json.dumps(
                {
                    "per_dimension": result_data["per_dimension"],
                    "question_breakdown": result_data["question_breakdown"],
                    "score_max": result_data["score_max"],
                }
            ),
        )
        self.db_session.add(ar)
        self.db_session.commit()
        self.db_session.refresh(ar)
        return ar

    def get_all_assessments_with_details(self) -> List[Dict[str, Any]]:
        """Retrieve all assessment results with employee and risk level details."""
        from APP.MODELS.employee import Employee

        results = (
            self.db_session.query(AssessmentResult, Employee)
            .join(Employee, AssessmentResult.employee_id == Employee.id)
            .order_by(AssessmentResult.created_at.desc())
            .all()
        )

        items = []
        for ar, emp in results:
            details = {}
            try:
                details = json.loads(ar.details_json) if ar.details_json else {}
            except Exception:
                pass

            # Extract risk level from details_json if risk_level_id is text
            risk_label = (
                ar.risk_level_id
                if isinstance(ar.risk_level_id, str)
                else f"Risk Level {ar.risk_level_id}"
            )
            if "risk_level" in details:
                risk_label = details["risk_level"]

            items.append(
                {
                    "id": ar.id,
                    "employee_id": emp.id,
                    "employee_name": emp.name,
                    "score_total": ar.score_total,
                    "score_percent": ar.score_percent,
                    "risk_level": risk_label,
                    "risk_level_id": ar.risk_level_id,
                    "created_at": ar.created_at,
                    "per_dimension": details.get("per_dimension", {}),
                    "score_max": details.get("score_max", 0),
                }
            )
        return items

    def process_all_assessments(self):
        """Processes all assessments in the database."""

        employees_ids = (
            self.db_session.query(EmployeeResponse.employee_id).distinct().all()
        )

        for (employee_id,) in employees_ids:

            """Process assessments for a single employee."""

            responses = (
                self.db_session.query(EmployeeResponse)
                .filter(EmployeeResponse.employee_id == employee_id)
                .all()
            )

            if not responses:
                continue

            questions_inputs: List[QuestionInput] = []

            for resp in responses:
                question = (
                    self.db_session.query(Question)
                    .filter(Question.id == resp.question_id)
                    .first()
                )
                if not question:
                    continue
                questions_inputs.append(
                    QuestionInput(
                        id=question.id,
                        weight=float(question.weight),
                        answer_value=int(resp.answer_value),
                        dimension=question.dimension,
                        is_inverted=bool(question.is_inverted),
                    )
                )

            # calculate assessment result
            result = calculate_assessment(questions_inputs)

            # save in database AssessmentResult
            assessment_result = AssessmentResult(
                employee_id=employee_id,
                score_total=result["score_total"],
                score_percent=result["score_percent"],
                risk_level_id=result["risk_level"],
                details_json=json.dumps(result),
                created_at=datetime.now(),
            )
            self.db_session.add(assessment_result)
        self.db_session.commit()

    def get_all_grouped_responses(self) -> dict[int, List[EmployeeResponse]]:
        """Retrieve all employee responses grouped by employee ID."""

        rows = self.db_session.query(EmployeeResponse).all()

        grouped: Dict[Any, Any] = {}

        for row in rows:
            key = (row.employee_id, row.assessment_id)
            grouped.setdefault(key, []).append(row)
        return grouped
