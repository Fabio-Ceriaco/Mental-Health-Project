from APP.REPOSITORIES.dashboard_repository import DashboardRepository
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Dict, Any
import json
from APP.MODELS import Employee, EmployeeResponse, AssessmentResult, RiskLevel


class DashboardService:

    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def get_global_dashboard_data(self):
        """Fetches and formats global dashboard data including latest risk per employee,
        global risk distribution, and average risk by department."""

        latest = self.repo.get_latest_risk_per_employee()
        distribution = self.repo.get_global_risk_distribution()
        avg_by_department = self.repo.get_average_risk_by_department()

        return {
            "latest_per_employee": [
                {
                    "employee_id": emp.id,
                    "name": emp.name,
                    "email": emp.email,
                    "risk_level": ar.risk_level_id,
                    "score_percent": ar.score_percent,
                }
                for ar, emp in latest
            ],
            "global_distribution": [
                {"risk": risk, "total": total} for risk, total in distribution
            ],
            "average_by_department": [
                {"department": dept, "avg_risk": round(avg, 2)}
                for dept, avg in avg_by_department
            ],
        }

    def get_employee_dashboard(self, employee_id: int) -> Dict[str, Any]:
        """Aggregates all dashboard metrics and computes per-assessment results
        using the employee_response table."""

        # validate employee
        emp = (
            self.repo.db_session.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )

        # History through assessments
        assessment_results: List[AssessmentResult] = (
            self.repo.db_session.query(AssessmentResult)
            .filter(AssessmentResult.employee_id == employee_id)
            .order_by(AssessmentResult.created_at.asc())
            .all()
        )

        # Initialize history and dimension accumulators
        history: List[Dict[str, Any]] = []

        dim_acc: Dict[str, List[float]] = {
            "stress": [],
            "anxiety": [],
            "depression": [],
            "burnout": [],
        }

        scores: List[float] = []

        # Cache for risk level names by id to avoid repeated queries
        risk_name_cache: Dict[int, str] = {}

        for ar in assessment_results:
            try:
                details_obj: Any = (
                    ar.details_json
                    if isinstance(ar.details_json, dict)
                    else json.loads(ar.details_json or "{}")
                )
            except:
                details_obj: Any = {}

            per_dim: Any = details_obj.get("per_dimension", {})

            for dim in dim_acc.keys():
                val: float | None = None
                if isinstance(per_dim, dict) and dim in per_dim:
                    dval: Dict[Any, Any] = per_dim.get(dim)  # type: ignore
                    if isinstance(dval, dict) and "percent" in dval:  # type: ignore
                        try:
                            val = float(dval["percent"])
                        except:
                            val = None
                    elif isinstance(dval, (int, float)):
                        val = float(dval)
                if val is not None:
                    dim_acc[dim].append(val)

            score = float(getattr(ar, "score_percent", getattr(ar, "score_total", 0.0)))
            # Normalize risk level to a displayable string
            risk_level_obj = getattr(ar, "risk_level", None)
            risk_level_name: str
            if risk_level_obj is not None:
                # ORM relationship object; prefer its name if available
                name = getattr(risk_level_obj, "name", None)
                risk_level_name = name if isinstance(name, str) else str(risk_level_obj)
            else:
                rl_id = getattr(ar, "risk_level_id", None)
                if isinstance(rl_id, int):
                    if rl_id in risk_name_cache:
                        risk_level_name = risk_name_cache[rl_id]
                    else:
                        # Look up the name once and cache it; fallback to string id
                        rl = (
                            self.repo.db_session.query(RiskLevel)
                            .filter(RiskLevel.id == rl_id)
                            .first()
                        )
                        risk_level_name = (
                            rl.name if rl and isinstance(rl.name, str) else str(rl_id)
                        )
                        risk_name_cache[rl_id] = risk_level_name
                else:
                    risk_level_name = "Desconhecido"

            scores.append(score)

            max_assessment_score = float(max(scores)) if scores else 0.0
            history.append(
                {
                    "date": ar.created_at,
                    "score": score,
                    "risk_level": risk_level_name,
                    "max_assessment_score": max_assessment_score,
                }
            )

        # Compute per assessment via employee_response

        """ Group by assessment_id and date, and summarize answer_value.
        Etch entry corresponds to one assessment taken by the employee."""

        raw_responses = (
            self.repo.db_session.query(EmployeeResponse)
            .filter(EmployeeResponse.employee_id == employee_id)
            .order_by(EmployeeResponse.created_at.asc())
            .all()
        )

        assessment_map: Dict[Any, Dict[str, Any]] = {}

        # Build a map of assessment_id and created_at to their responses
        for resp in raw_responses:
            assess_id = getattr(resp, "assessment_id", None)
            created_at = getattr(resp, "created_at", None) or datetime.now()
            date_key = created_at.date().isoformat()  # Use date part only for grouping
            key = f"{assess_id}::{date_key}"

            if key not in assessment_map:
                assessment_map[key] = {
                    "assessment_id": assess_id,
                    "date": created_at,
                    "total_score": 0.0,
                    "answer_count": 0,
                    "responses": [],
                }

            val = getattr(resp, "answer_value", None)
            if val is None:
                try:
                    val = float(getattr(resp, "answer_value_raw", 0.0))

                except:
                    val = 0.0

            try:
                assessment_map[key]["total_score"] += float(val)
            except Exception:
                # if is str try convert else ignore
                try:
                    assessment_map[key]["total_score"] += float(str(val))
                except Exception:
                    pass
            question_id = getattr(
                resp, "question_id", getattr(resp, "assessment_question_id", None)
            )

            if question_id is None:
                raise ValueError("EmployeeResponse sem question_id")

            assessment_map[key]["answer_count"] += 1
            assessment_map[key]["responses"].append(
                {"question_id": question_id, "value": float(val)}
            )

        per_assessment_results = sorted(
            assessment_map.values(), key=lambda x: x["date"]
        )

        # Overall aggregates
        total_assessments = len(history)  # number of assessments taken
        avg_score = float(sum(scores) / total_assessments) if total_assessments else 0.0
        max_score = float(max(scores)) if scores else 0.0
        min_score = float(min(scores)) if scores else 0.0
        last_score = float(scores[-1]) if scores else 0.0
        last_risk = history[-1]["risk_level"] if history else "Desconhecido"

        # Compute per-dimension
        per_dimension: Dict[Any, Any] = {}
        for dim, vals in dim_acc.items():
            per_dimension[dim] = {
                "percent": round(float(sum(vals) / len(vals)), 2) if vals else 0.0
            }

        # Determine top dimension
        try:
            top_dimension: Any = max(
                per_dimension.items(), key=lambda x: x[1]["percent"]
            )[0]
        except Exception:
            top_dimension = None

        overall: Dict[str, Any] = {
            "score_total": round(last_score, 2),
            "risk_level": last_risk,
            "max_score": round(max_score, 2),
        }

        totals: Dict[str, Any] = {
            "total_assessments": total_assessments,
            "avg_score": round(avg_score, 2),
            "max_score": round(max_score, 2),
            "min_score": round(min_score, 2),
        }

        return {
            "employee_id": employee_id,
            "history": history,
            "per_dimension": per_dimension,
            "overall": overall,
            "totals": totals,
            "top_dimension": top_dimension,
            "per_assessment_results": per_assessment_results,
        }
