import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from APP.MODELS import AssessmentResult, Employee, Department
from APP.REPOSITORIES.base_repository import BaseRepository


class DashboardRepository(BaseRepository):
    """Repository for dashboard-related database operations."""

    def __init__(self, db_session: Session):
        super().__init__(db_session, AssessmentResult)

    # current status for employees
    def get_latest_risk_per_employee(self):
        """Retrieve the latest risk level for each employee."""

        # suquery to get the latest assessment date per employee
        subquery = (
            self.db_session.query(
                AssessmentResult.employee_id,
                func.max(AssessmentResult.created_at).label("last_date"),
            )
            .group_by(AssessmentResult.employee_id)
            .subquery()
        )

        # Join with AssessmentResult and Employees to get the latest risk levels
        return (
            (
                self.db_session.query(AssessmentResult, Employee).join(
                    subquery,
                    (AssessmentResult.employee_id == subquery.c.employee_id)
                    & (AssessmentResult.created_at == subquery.c.last_date),
                )
            )
            .join(Employee, Employee.id == AssessmentResult.employee_id)
            .all()
        )

    def get_global_risk_distribution(self):
        """Retrieve the distribution of risk levels across all employees."""

        return (
            self.db_session.query(
                AssessmentResult.risk_level, func.count(AssessmentResult.id)
            )
            .group_by(AssessmentResult.risk_level)
            .all()
        )

    def get_average_risk_by_department(self):
        """Retrieve the average risk level per department."""

        # Join Employees and Departments to get average risk per department
        return (
            self.db_session.query(
                Department.name, func.avg(AssessmentResult.score_percent)
            )
            .join(Employee, Employee.department_id == Department.id)
            .join(AssessmentResult, AssessmentResult.employee_id == Employee.id)
            .group_by(Department.name)
            .all()
        )

    def get_per_dimension_risk_by_department(self):
        """
        Retrieve per-dimension average risk per department, along with overall average.
        Returns a list of dicts with keys: department, avg_risk, avg_stress, avg_burnout,
        avg_anxiety, avg_depression, and optionally other dimensions if present.
        """

        # Query all assessments joined to employees and departments
        rows = (
            self.db_session.query(
                Department.name.label("department"),
                AssessmentResult.details_json,
                AssessmentResult.score_percent,
            )
            .join(Employee, Employee.department_id == Department.id)
            .join(AssessmentResult, AssessmentResult.employee_id == Employee.id)
            .all()
        )

        # Aggregators per department
        agg: Dict[str, Dict[str, float]] = {}
        counts: Dict[str, Dict[str, int]] = {}
        overall_totals: Dict[str, float] = {}
        overall_counts: Dict[str, int] = {}

        def _extract_numeric(val: Any) -> Optional[float]:
            try:
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, dict):
                    p = val.get("percent")
                    if isinstance(p, (int, float)):
                        return float(p)
            except Exception:
                pass
            return None

        for dept_name, details_json, score_percent in rows:
            if dept_name not in agg:
                agg[dept_name] = {}
                counts[dept_name] = {}
                overall_totals[dept_name] = 0.0
                overall_counts[dept_name] = 0

            # overall risk
            try:
                if score_percent is not None:
                    overall_totals[dept_name] += float(score_percent)
                    overall_counts[dept_name] += 1
            except Exception:
                pass

            # per-dimension from details_json
            if details_json:
                try:
                    data = json.loads(details_json)
                    if isinstance(data, dict):
                        for dim_key, dim_val in data.items():
                            num = _extract_numeric(dim_val)
                            if num is None:
                                continue
                            agg[dept_name][dim_key] = (
                                agg[dept_name].get(dim_key, 0.0) + num
                            )
                            counts[dept_name][dim_key] = (
                                counts[dept_name].get(dim_key, 0) + 1
                            )
                except Exception:
                    # ignore malformed json
                    continue

        # Build results
        results: List[Dict[str, Any]] = []
        for dept_name in agg.keys() | overall_totals.keys():
            record: Dict[str, Any] = {"department": dept_name}
            # overall
            oc = overall_counts.get(dept_name, 0)
            ot = overall_totals.get(dept_name, 0.0)
            record["avg_risk"] = float(ot / oc) if oc > 0 else 0.0

            # known dimensions: include common ones if present
            for key in [
                "stress",
                "burnout",
                "anxiety",
                "depression",
                "sono",
                "turnos",
                "ergonomia",
                "geral",
            ]:
                c = counts.get(dept_name, {}).get(key, 0)
                t = agg.get(dept_name, {}).get(key, 0.0)
                if c > 0:
                    record[f"avg_{key}"] = float(t / c)

            results.append(record)

        return results

    def get_employee_risk_history(self, employee_id: int):
        """Retrieve the risk history for a specific employee."""

        # Query AssessmentResult for the given employee_id ordered by creation date
        return (
            self.db_session.query(AssessmentResult)
            .filter(AssessmentResult.employee_id == employee_id)
            .order_by(AssessmentResult.created_at)
            .all()
        )

    def get_per_dimension_averages(
        self, employee_id: int, as_percent: bool = True
    ) -> Dict[str, Any]:
        """Retrieve per-dimension scores for a specific employee."""

        # query to get all assessment results for the employee
        results = (
            self.db_session.query(
                AssessmentResult.details_json
            )  # assuming details_json contains per-dimension scores
            .filter(AssessmentResult.employee_id == employee_id)
            .all()
        )

        dim_totals: Dict[str, float] = {}
        dim_counts: Dict[str, int] = {}

        for r in results:
            if not r.details_json:
                continue
            try:
                data = json.loads(r.details_json)
            except json.JSONDecodeError:
                continue

            for dim, val in data.items():
                if not isinstance(val, (int, float)):
                    continue

                dim_totals[dim] = dim_totals.get(dim, 0) + val
                dim_counts[dim] = dim_counts.get(dim, 0) + 1
        per_dimension: Dict[str, Any] = {}
        for dim in dim_totals:
            count = dim_counts.get(dim, 1)  # avoid division by zero
            avg = dim_totals[dim] / count  # calculate average
            if as_percent:
                # convert to percent
                per_dimension[dim] = {"percent": round(avg, 2)}

        return per_dimension

    def get_overall(self, employee_id: int) -> Dict[str, Any]:
        """Retrieve overall average score for a specific employee."""

        avg_score = (
            self.db_session.query(func.avg(AssessmentResult.score_percent))
            .filter(AssessmentResult.employee_id == employee_id)
            .scalar()
        )

        # query to get average score and most frequent risk level
        risk = (
            self.db_session.query(
                AssessmentResult.risk_level_id,
                func.count(AssessmentResult.risk_level_id).label("count"),
            )
            .filter(AssessmentResult.employee_id == employee_id)
            .group_by(AssessmentResult.risk_level_id)
            .order_by(func.count(AssessmentResult.risk_level_id).desc())
            .first()
        )

        return {
            "score_total": round(float(avg_score), 2) if avg_score else 0,
            "risk_level": str(risk[0]) if risk else None,
        }
