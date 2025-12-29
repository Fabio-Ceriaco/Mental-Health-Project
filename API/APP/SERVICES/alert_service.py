from typing import Any, Dict, Optional, Iterable
from sqlalchemy.orm import Session

from APP.REPOSITORIES.alert_repository import AlertRepository
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult
from APP.MODELS.employeeResponse import EmployeeResponse
from APP.MODELS.question import Question
from APP.ml.ml_service import PredictService


class AlertService:
    def __init__(self, db: Session):
        self.repo = AlertRepository(db)

    def get_summary(self) -> Dict[str, Any]:
        by_type = self.repo.counts_by_type()
        statuses = self.repo.status_buckets()

        # Only include actual harassment alerts (Assédio Moral, Assédio Sexual)
        harassment = [
            item
            for item in by_type
            if any(
                k in (item.get("label") or "").lower() for k in ["assédio", "assedio"]
            )
        ]

        return {
            "harassment": harassment,
            "statuses": {
                "A Aguardar": statuses.get("waiting", 0),
                "Em Andamento": statuses.get("in_progress", 0),
                "Realizados": statuses.get("done", 0),
            },
        }

    def list_recent(self, limit: int = 20) -> Dict[str, Any]:
        items = self.repo.list_recent(limit=limit)
        return {"items": items, "total": len(items)}

    def seed_alert_types_default(self) -> Dict[str, Any]:
        defaults = [
            ("Risco Saúde Mental", 3, "Risco identificado por predição ML"),
            ("Assédio Moral", 4, "Possível assédio moral"),
            ("Assédio Sexual", 5, "Possível assédio sexual"),
        ]
        created = []
        for name, sev, desc in defaults:
            atype = self.repo.get_or_create_alert_type(
                name, severity_level=sev, description=desc
            )
            created.append(
                {
                    "id": atype.id,
                    "name": atype.name,
                    "severity_level": atype.severity_level,
                }
            )
        return {"created_or_existing": created}

    def generate_alerts_from_assessments(self) -> Dict[str, Any]:
        """Generate alerts from ML predictions for all employees with assessments."""
        ml_service = PredictService(self.repo.db)

        # Collect unique employee ids that have assessments
        emp_ids = [
            row.employee_id
            for row in self.repo.db.query(AssessmentResult.employee_id).distinct().all()
        ]

        if not emp_ids:
            return {"generated": 0, "reason": "No employees with assessments found"}

        generated = 0
        skipped = 0
        harassment_generated = 0

        for emp_id in emp_ids:
            try:
                emp = self.repo.db.query(Employee).filter(Employee.id == emp_id).first()
                if not emp:
                    continue

                # Get most recent assessment result for this employee to retrieve actual score
                latest_result = (
                    self.repo.db.query(AssessmentResult)
                    .filter(AssessmentResult.employee_id == emp_id)
                    .order_by(AssessmentResult.created_at.desc())
                    .first()
                )
                score_percent = latest_result.score_percent if latest_result else 0.0

                # Use enhanced ML model for prediction
                pred = ml_service.predict_employee(emp_id)
                prediction = (
                    pred.get("prediction", {}) if isinstance(pred, dict) else {}
                )
                predicted_level = int(prediction.get("predicted_risk_level", 0))
                risk_label = prediction.get(
                    "risk_label", f"Risk Level {predicted_level}"
                )
                created = self.create_from_prediction(
                    employee=emp,
                    predicted_level=predicted_level,
                    risk_label=risk_label,
                    score_percent=score_percent,
                )
                if created:
                    generated += 1
                else:
                    skipped += 1

                # Harassment alerts based on stored responses answered "Sempre"
                rows = (
                    self.repo.db.query(EmployeeResponse, Question)
                    .join(Question, EmployeeResponse.question_id == Question.id)
                    .filter(EmployeeResponse.employee_id == emp_id)
                    .filter(EmployeeResponse.answer_value >= 4)
                    .all()
                )
                harassment_generated += self._create_harassment_from_rows(emp, rows)
            except Exception:
                # Skip failures per employee to keep batch running
                continue

        return {
            "generated": generated,
            "skipped": skipped,
            "harassment_generated": harassment_generated,
            "employees_processed": len(emp_ids),
        }

    def create_from_prediction(
        self,
        *,
        employee: Employee,
        predicted_level: int,
        risk_label: str,
        score_percent: float,
    ) -> Dict[str, Any]:
        # Only generate alerts for predicted levels above 4
        if predicted_level <= 4:
            return {}

        # Map predicted level to severity and friendly type
        severity = int(predicted_level) if predicted_level else 1
        type_name = "Risco Saúde Mental"
        description = f"{risk_label} detectado (predição ML)"
        atype = self.repo.get_or_create_alert_type(
            type_name, severity_level=severity, description=description
        )

        message = (
            f"{risk_label} detectado na última avaliação (score {score_percent:.1f}%)."
        )
        alert = self.repo.create_alert(
            alert_type_id=atype.id,
            department_id=employee.department_id or 0,
            employee_id=employee.id,
            message=message,
            is_resolved=False,
        )
        return {
            "id": alert.id,
            "type": atype.name,
            "severity_level": atype.severity_level,
            "message": alert.message,
        }

    def create_harassment_alerts_from_responses(
        self,
        *,
        employee: Employee,
        responses: Iterable[Any],
        question_map: Dict[int, Question],
    ) -> int:
        """Create harassment alerts when answer_value corresponds to "Sempre" (>=4) on harassment-related questions."""

        created = 0
        seen_types = set()
        for resp in responses:
            qid = getattr(resp, "question_id", None) or resp.get("question_id")  # type: ignore
            ans = getattr(resp, "answer_value", None) or resp.get("answer_value")  # type: ignore
            if ans is None or qid is None:
                continue
            if float(ans) < 4:
                continue  # only "Sempre"
            qobj = question_map.get(int(qid)) if question_map else None
            if not qobj:
                continue
            text_lower = (qobj.text or "").lower()
            if "assédio" not in text_lower and "assedio" not in text_lower:
                continue
            is_sexual = "sexual" in text_lower
            type_name = "Assédio Sexual" if is_sexual else "Assédio Moral"
            if type_name in seen_types:
                continue
            msg = f"Resposta 'Sempre' em pergunta de assédio: {qobj.text[:120]}"
            self._create_harassment_alert(
                employee=employee, message=msg, is_sexual=is_sexual
            )
            seen_types.add(type_name)
            created += 1
        return created

    def _create_harassment_alert(
        self,
        *,
        employee: Employee,
        message: str,
        is_sexual: bool,
    ) -> Dict[str, Any]:
        type_name = "Assédio Sexual" if is_sexual else "Assédio Moral"
        severity = 5 if is_sexual else 4
        description = (
            "Possível assédio sexual" if is_sexual else "Possível assédio moral"
        )
        atype = self.repo.get_or_create_alert_type(
            type_name, severity_level=severity, description=description
        )
        alert = self.repo.create_alert(
            alert_type_id=atype.id,
            department_id=employee.department_id or 0,
            employee_id=employee.id,
            message=message,
            is_resolved=False,
        )
        return {
            "id": alert.id,
            "type": atype.name,
            "severity_level": atype.severity_level,
            "message": alert.message,
        }

    def _create_harassment_from_rows(
        self, employee: Employee, rows: Iterable[Any]
    ) -> int:
        created = 0
        seen_types = set()
        for eresp, qobj in rows:
            if not qobj:
                continue
            if float(eresp.answer_value or 0) < 4:
                continue
            text_lower = (qobj.text or "").lower()
            if "assédio" not in text_lower and "assedio" not in text_lower:
                continue
            is_sexual = "sexual" in text_lower
            type_name = "Assédio Sexual" if is_sexual else "Assédio Moral"
            if type_name in seen_types:
                continue
            msg = f"Resposta 'Sempre' em pergunta de assédio: {qobj.text[:120]}"
            self._create_harassment_alert(
                employee=employee, message=msg, is_sexual=is_sexual
            )
            seen_types.add(type_name)
            created += 1
        return created
