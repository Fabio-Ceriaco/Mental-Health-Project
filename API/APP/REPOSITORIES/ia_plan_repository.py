from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from APP.MODELS.ia_improve_plan import IAImprovePlan
from APP.MODELS.ia_impact_eval import IAImpactEval
from APP.MODELS.department import Department
from APP.MODELS.action_department import ActionDepartment
from APP.MODELS.action import Action
from APP.MODELS.status import Status
from typing import List, Optional, Dict, Any
from datetime import datetime


class IAPlanRepository:
    """Repository for IA Improve Plan operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """Get all IA improve plans with related data"""
        plans = (
            self.db.query(IAImprovePlan)
            .options(
                joinedload(IAImprovePlan.department),
                joinedload(IAImprovePlan.action_department).joinedload(
                    ActionDepartment.action
                ),
                joinedload(IAImprovePlan.status),
                joinedload(IAImprovePlan.impact_evaluation),
            )
            .order_by(desc(IAImprovePlan.created_at))
            .all()
        )

        result = []
        for plan in plans:
            # Get impact evaluation if exists
            impact_data = None
            if plan.impact_evaluation:
                impact_eval = (
                    plan.impact_evaluation[0] if plan.impact_evaluation else None
                )
                if impact_eval:
                    impact_data = {
                        "before_index": impact_eval.before_index,
                        "after_index": impact_eval.after_index,
                        "evaluation_date": (
                            impact_eval.evaluation_date.isoformat()
                            if impact_eval.evaluation_date
                            else None
                        ),
                    }

            result.append(
                {
                    "id": plan.id,
                    "department_id": plan.department_id,
                    "department_name": (
                        plan.department.name if plan.department else None
                    ),
                    "action_id": (
                        plan.action_department.action_id
                        if plan.action_department
                        else None
                    ),
                    "action_name": (
                        plan.action_department.action.name
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                    "action_description": (
                        plan.action_department.action.description
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                    "status_id": plan.status_id,
                    "status_name": plan.status.name if plan.status else None,
                    "created_at": (
                        plan.created_at.isoformat() if plan.created_at else None
                    ),
                    "updated_at": (
                        plan.updated_at.isoformat() if plan.updated_at else None
                    ),
                    "impact_evaluation": impact_data,
                }
            )

        return result

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific IA improve plan by ID"""
        plan = (
            self.db.query(IAImprovePlan)
            .options(
                joinedload(IAImprovePlan.department),
                joinedload(IAImprovePlan.action_department).joinedload(
                    ActionDepartment.action
                ),
                joinedload(IAImprovePlan.status),
                joinedload(IAImprovePlan.impact_evaluation),
            )
            .filter(IAImprovePlan.id == plan_id)
            .first()
        )

        if not plan:
            return None

        impact_data = None
        if plan.impact_evaluation:
            impact_eval = plan.impact_evaluation[0] if plan.impact_evaluation else None
            if impact_eval:
                impact_data = {
                    "before_index": impact_eval.before_index,
                    "after_index": impact_eval.after_index,
                    "evaluation_date": (
                        impact_eval.evaluation_date.isoformat()
                        if impact_eval.evaluation_date
                        else None
                    ),
                }

        return {
            "id": plan.id,
            "department_id": plan.department_id,
            "department_name": plan.department.name if plan.department else None,
            "action_id": (
                plan.action_department.action_id if plan.action_department else None
            ),
            "action_name": (
                plan.action_department.action.name
                if plan.action_department and plan.action_department.action
                else None
            ),
            "action_description": (
                plan.action_department.action.description
                if plan.action_department and plan.action_department.action
                else None
            ),
            "status_id": plan.status_id,
            "status_name": plan.status.name if plan.status else None,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
            "impact_evaluation": impact_data,
        }

    def get_plans_by_department(self, department_id: int) -> List[Dict[str, Any]]:
        """Get all plans for a specific department"""
        plans = (
            self.db.query(IAImprovePlan)
            .options(
                joinedload(IAImprovePlan.department),
                joinedload(IAImprovePlan.action_department).joinedload(
                    ActionDepartment.action
                ),
                joinedload(IAImprovePlan.status),
                joinedload(IAImprovePlan.impact_evaluation),
            )
            .filter(IAImprovePlan.department_id == department_id)
            .order_by(desc(IAImprovePlan.created_at))
            .all()
        )

        result = []
        for plan in plans:
            impact_data = None
            if plan.impact_evaluation:
                impact_eval = (
                    plan.impact_evaluation[0] if plan.impact_evaluation else None
                )
                if impact_eval:
                    impact_data = {
                        "before_index": impact_eval.before_index,
                        "after_index": impact_eval.after_index,
                        "evaluation_date": (
                            impact_eval.evaluation_date.isoformat()
                            if impact_eval.evaluation_date
                            else None
                        ),
                    }

            result.append(
                {
                    "id": plan.id,
                    "department_id": plan.department_id,
                    "department_name": (
                        plan.department.name if plan.department else None
                    ),
                    "action_id": (
                        plan.action_department.action_id
                        if plan.action_department
                        else None
                    ),
                    "action_name": (
                        plan.action_department.action.name
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                    "action_description": (
                        plan.action_department.action.description
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                    "status_id": plan.status_id,
                    "status_name": plan.status.name if plan.status else None,
                    "created_at": (
                        plan.created_at.isoformat() if plan.created_at else None
                    ),
                    "updated_at": (
                        plan.updated_at.isoformat() if plan.updated_at else None
                    ),
                    "impact_evaluation": impact_data,
                }
            )

        return result

    def update_plan_status(
        self, plan_id: int, status_id: int
    ) -> Optional[Dict[str, Any]]:
        """Update the status of an IA improve plan"""
        plan = self.db.query(IAImprovePlan).filter(IAImprovePlan.id == plan_id).first()

        if not plan:
            return None

        plan.status_id = status_id
        self.db.commit()
        self.db.refresh(plan)

        return self.get_plan_by_id(plan_id)

    def create_impact_evaluation(
        self, plan_id: int, before_index: float, after_index: float
    ) -> Optional[Dict[str, Any]]:
        """Create an impact evaluation for a plan"""
        # Check if plan exists
        plan = self.db.query(IAImprovePlan).filter(IAImprovePlan.id == plan_id).first()
        if not plan:
            return None

        impact_eval = IAImpactEval(
            plan_id=plan_id,
            before_index=before_index,
            after_index=after_index,
            evaluation_date=datetime.now(),
        )

        self.db.add(impact_eval)
        self.db.commit()
        self.db.refresh(impact_eval)

        return {
            "id": impact_eval.id,
            "plan_id": impact_eval.plan_id,
            "before_index": impact_eval.before_index,
            "after_index": impact_eval.after_index,
            "evaluation_date": impact_eval.evaluation_date.isoformat(),
        }
