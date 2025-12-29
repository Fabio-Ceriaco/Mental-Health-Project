import numpy as np
from datetime import datetime, timedelta
from APP.REPOSITORIES.department_repository import DepartmentRepository
from APP.MODELS import AssessmentResult, Employee
from sqlalchemy.orm import Session
from typing import Dict, List


class DepartmentMetricsService:
    """Service to calculate and update department metrics based on employees assessments."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.department_repo = DepartmentRepository(db_session)

    def reclac_department_metrics(self, department_id: int, months: int = 12):
        """Recalculates and updates the metrics fro a given department over a specified time frame."""

        cutoff = datetime.now() - timedelta(
            days=30 * months
        )  # approximate month calculation

        # Fetch assessments for employees in the department within the time frame
        assessments = (
            self.db_session.query(AssessmentResult)
            .join(Employee, Employee.id == AssessmentResult.employee_id)
            .filter(Employee.department_id == department_id)
            .filter(AssessmentResult.created_at >= cutoff)
            .all()
        )

        # extract per dimension scores from details_json
        dims: Dict[str, List[float]] = {}

        # aggregate scores per dimension
        for a in assessments:
            try:
                import json

                per_dim = json.loads(a.details_json).get("per_dimension", {})
            except Exception:
                per_dim = {}
            for dim, score in per_dim.items():
                dims.setdefault(dim, []).append(score.get("score_percent", 0.0))

        metrics: Dict[str, float] = {}

        # Calculate average and percentiles for each dimension
        for dim, scores in dims.items():
            arr = np.array(scores)
            if arr.size == 0:
                continue
            metrics[f"{dim}_mean"] = float(np.mean(arr))  # average
            metrics[f"{dim}_p25"] = float(np.percentile(arr, 25))  # 25th percentile
            metrics[f"{dim}_p50"] = float(
                np.percentile(arr, 50)
            )  # median or 50th percentile
            metrics[f"{dim}_p75"] = float(np.percentile(arr, 75))  # 75th percentile

        # Upsert the calculated metrics into the database
        return self.department_repo.upsert_metrics(department_id, metrics)
