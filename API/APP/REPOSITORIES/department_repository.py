from sqlalchemy.orm import Session
from APP.MODELS import DepartmentMetric
from APP.REPOSITORIES.base_repository import BaseRepository
from typing import Dict


class DepartmentRepository(BaseRepository):
    """Repository for managing Department data in the database."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, DepartmentMetric)

    def upsert_metrics(
        self, department_id: int, metrics: Dict[str, float]
    ) -> DepartmentMetric:
        """Upset department metrics in the database."""

        dm = DepartmentMetric(
            department_id=department_id,
            anxiety_avg=metrics.get("anxiety_avg", 0.0),
            depression_avg=metrics.get("depression_avg", 0.0),
            stress_avg=metrics.get("stress_avg", 0.0),
            burnout_avg=metrics.get("burnout_avg", 0.0),
            percentile_25=metrics.get("percentile_25", None),
            percentile_50=metrics.get("percentile_50", None),
            percentile_75=metrics.get("percentile_75", None),
            metric_status_id=metrics.get("metric_status_id", 1),  # default status
        )

        self.db_session.add(dm)
        self.db_session.commit()
        self.db_session.refresh(dm)
        return dm
