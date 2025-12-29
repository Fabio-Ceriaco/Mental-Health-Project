"""
AI Improvement Plan Service
Generates AI-driven improvement plans for departments with high-risk metrics.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from APP.MODELS.department import Department
from APP.MODELS.action import Action
from APP.MODELS.action_department import ActionDepartment
from APP.MODELS.ia_improve_plan import IAImprovePlan
from APP.MODELS.status import Status
from APP.MODELS.ia_impact_eval import IAImpactEval
from APP.REPOSITORIES.dashboard_repository import DashboardRepository


class AIImprovementService:
    """Service to generate and manage AI-driven improvement plans"""

    THRESHOLD = 60.0  # Percentage threshold for triggering improvements

    # Dimension names mapping
    DIMENSION_NAMES = {
        "stress": "Stress",
        "burnout": "Burnout",
        "anxiety": "Ansiedade",
        "depression": "Depressão",
        "sono": "Sono",
        "turnos": "Turnos",
        "ergonomia": "Ergonomia",
        "geral": "Bem-estar Geral",
    }

    def __init__(self, db: Session):
        self.db = db

    def check_and_generate_plans(
        self, threshold: Optional[float] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Check all departments for metrics exceeding threshold
        and generate improvement plans where needed.
        """
        dashboard_repo = DashboardRepository(self.db)

        # Get department averages (overall risk per department)
        # Note: This returns a list of tuples (department_name, avg_risk)
        # If a richer per-dimension method is added later, this code will
        # gracefully handle dict records as well.
        # Prefer per-dimension aggregation to detect specific thresholds
        try:
            dept_averages = dashboard_repo.get_per_dimension_risk_by_department()
        except Exception:
            # Fallback to overall average only
            dept_averages = dashboard_repo.get_average_risk_by_department()

        thresh = float(threshold) if threshold is not None else self.THRESHOLD

        results = {
            "checked_departments": 0,
            "plans_generated": 0,
            "departments_at_risk": [],
            "generated_plans": [],
        }

        for dept_data in dept_averages:
            results["checked_departments"] += 1

            # Support both tuple records (name, avg) and dict records
            dept_name: Optional[str] = None
            avg_risk: float = 0.0
            dept_record: Dict[str, Any] = {}

            if isinstance(dept_data, tuple) and len(dept_data) >= 2:
                dept_name = dept_data[0]
                try:
                    avg_risk = float(dept_data[1] or 0)
                except Exception:
                    avg_risk = 0.0
                dept_record = {"department": dept_name, "avg_risk": avg_risk}
            elif isinstance(dept_data, dict):
                dept_name = dept_data.get("department")
                avg_risk = float(dept_data.get("avg_risk", 0) or 0)
                dept_record = dept_data
            else:
                # Unknown record shape; skip safely
                continue

            # Get department from database
            department = (
                self.db.query(Department).filter(Department.name == dept_name).first()
            )
            if not department:
                continue

            # Check each dimension (if per-dimension metrics are available)
            dimensions_to_improve: List[tuple[str, float]] = []

            if dept_record.get("avg_stress", 0) > thresh:
                dimensions_to_improve.append(("stress", dept_record["avg_stress"]))
            if dept_record.get("avg_burnout", 0) > thresh:
                dimensions_to_improve.append(("burnout", dept_record["avg_burnout"]))
            if dept_record.get("avg_anxiety", 0) > thresh:
                dimensions_to_improve.append(("anxiety", dept_record["avg_anxiety"]))
            if dept_record.get("avg_depression", 0) > thresh:
                dimensions_to_improve.append(
                    ("depression", dept_record["avg_depression"])
                )

            # Fallback: if no per-dimension data, use overall risk
            if not dimensions_to_improve and avg_risk > thresh:
                dimensions_to_improve.append(("geral", avg_risk))

            if dimensions_to_improve:
                results["departments_at_risk"].append(
                    {"department": dept_name, "dimensions": dimensions_to_improve}
                )

                # Generate improvement plan for each dimension
                if not dry_run:
                for dimension, value in dimensions_to_improve:
                    plan = self._generate_improvement_plan(
                        department, dimension, value, dept_record, thresh
                    )
                    if plan:
                        results["plans_generated"] += 1
                        results["generated_plans"].append(
                            {
                                "plan_id": plan.id,
                                "department": dept_name,
                                "dimension": dimension,
                                "value": value,
                            }
                        )

        return results

    def _generate_improvement_plan(
        self,
        department: Department,
        dimension: str,
        value: float,
        dept_data: Dict[str, Any],
        threshold: float,
    ) -> Optional[IAImprovePlan]:
        """
        Generate an improvement plan for a specific department and dimension.
        """

        # Check if plan already exists for this department and dimension
        existing_plan = self._check_existing_plan(department.id, dimension)
        if existing_plan:
            return existing_plan

        # Generate AI recommendations
        action_data = self._generate_ai_recommendations(
            department.name, dimension, value, dept_data, threshold
        )

        # Create action
        action = Action(
            name=action_data["name"],
            description=action_data["description"],
            start_date=datetime.now(),
            is_active=True,
        )
        self.db.add(action)
        self.db.flush()  # Get action ID

        # Link action to department
        action_department = ActionDepartment(
            action_id=action.id,
            department_id=department.id,
            date_assigned=datetime.now(),
            is_active=True,
        )
        self.db.add(action_department)
        self.db.flush()  # Get action_department ID

        # Get "Pendente" status
        status = self.db.query(Status).filter(Status.name == "Pendente").first()
        if not status:
            # Create default status if not exists
            status = Status(name="Pendente")
            self.db.add(status)
            self.db.flush()

        # Create improvement plan
        improve_plan = IAImprovePlan(
            department_id=department.id,
            action_department_id=action_department.id,
            status_id=status.id,
        )
        self.db.add(improve_plan)
        self.db.commit()

        return improve_plan

    def _check_existing_plan(
        self, department_id: int, dimension: str
    ) -> Optional[IAImprovePlan]:
        """
        Check if an active improvement plan already exists for this department and dimension.
        """
        # Get recent plans (last 30 days) for this department
        from datetime import timedelta

        recent_date = datetime.now() - timedelta(days=30)

        existing_plans = (
            self.db.query(IAImprovePlan)
            .join(ActionDepartment)
            .join(Action)
            .filter(
                IAImprovePlan.department_id == department_id,
                IAImprovePlan.created_at >= recent_date,
                Action.description.contains(
                    dimension
                ),  # Check if dimension is in description
            )
            .first()
        )

        return existing_plans

    def _generate_ai_recommendations(
        self,
        department_name: str,
        dimension: str,
        value: float,
        dept_data: Dict[str, Any],
        threshold: float,
    ) -> Dict[str, str]:
        """
        Generate AI-powered recommendations using a structured prompt.
        This is a placeholder for actual AI integration (OpenAI, etc.)
        """

        dimension_display = self.DIMENSION_NAMES.get(dimension, dimension)

        # Build context for AI
        prompt_context = f"""
Departamento: {department_name}
Dimensão crítica: {dimension_display}
Valor atual: {value:.1f}%
    Limiar de alerta: {threshold}%

Métricas do departamento:
- Stress médio: {dept_data.get('avg_stress', 0):.1f}%
- Burnout médio: {dept_data.get('avg_burnout', 0):.1f}%
- Ansiedade média: {dept_data.get('avg_anxiety', 0):.1f}%
- Depressão média: {dept_data.get('avg_depression', 0):.1f}%
- Score global: {dept_data.get('avg_risk', 0):.1f}%

Objetivo: Criar um plano de melhoria para reduzir {dimension_display} e melhorar a saúde mental dos colaboradores.
"""

        # For now, generate rule-based recommendations
        # In production, you would call an AI API here
        recommendations = self._get_rule_based_recommendations(dimension, value)

        return {
            "name": recommendations["name"],
            "description": f"{recommendations['description']}\n\nContexto: {dimension_display} em {value:.1f}% (acima do limiar de {threshold}%)",
            "prompt_used": prompt_context,
        }

    def _get_rule_based_recommendations(
        self, dimension: str, value: float
    ) -> Dict[str, str]:
        """
        Generate rule-based recommendations based on dimension and severity.
        """

        severity = (
            "crítico" if value >= 75 else "elevado" if value >= 65 else "moderado"
        )

        recommendations = {
            "stress": {
                "name": f"Programa de Gestão de Stress - Nível {severity.capitalize()}",
                "description": "Implementar sessões de mindfulness, técnicas de relaxamento, gestão de tempo e carga de trabalho. Promover pausas regulares e ambiente de trabalho equilibrado.",
            },
            "burnout": {
                "name": f"Prevenção de Burnout - Intervenção {severity.capitalize()}",
                "description": "Revisão de cargas de trabalho, implementação de horários flexíveis, programas de reconhecimento e apoio psicológico. Promover equilíbrio vida-trabalho.",
            },
            "anxiety": {
                "name": f"Apoio para Ansiedade - Prioridade {severity.capitalize()}",
                "description": "Sessões de psicologia, workshops de gestão de ansiedade, criação de ambiente seguro e acolhedor. Reduzir fatores de stress organizacional.",
            },
            "depression": {
                "name": f"Programa de Bem-Estar Mental - Urgência {severity.capitalize()}",
                "description": "Acompanhamento psicológico especializado, grupos de apoio, atividades de integração social. Cultura organizacional de apoio mútuo.",
            },
        }

        default = {
            "name": f"Plano de Melhoria de Bem-Estar - {severity.capitalize()}",
            "description": f"Implementar medidas de melhoria focadas em {self.DIMENSION_NAMES.get(dimension, dimension)}. Incluir formações, apoio especializado e mudanças organizacionais.",
        }

        return recommendations.get(dimension, default)

    def evaluate_plan_impact(
        self, plan_id: int, before_index: float, after_index: float
    ) -> Optional[IAImpactEval]:
        """
        Evaluate the impact of an implemented improvement plan.
        """

        # Check if plan exists
        plan = self.db.query(IAImprovePlan).filter(IAImprovePlan.id == plan_id).first()
        if not plan:
            return None

        # Check if evaluation already exists
        existing_eval = (
            self.db.query(IAImpactEval).filter(IAImpactEval.plan_id == plan_id).first()
        )

        if existing_eval:
            # Update existing evaluation
            existing_eval.after_index = after_index
            existing_eval.evaluation_date = datetime.now()
            self.db.commit()
            return existing_eval

        # Create new evaluation
        impact_eval = IAImpactEval(
            plan_id=plan_id,
            before_index=before_index,
            after_index=after_index,
            evaluation_date=datetime.now(),
        )

        self.db.add(impact_eval)

        # Update plan status to "Concluído" if improvement is significant
        if after_index < before_index:
            completed_status = (
                self.db.query(Status).filter(Status.name == "Concluído").first()
            )
            if completed_status:
                plan.status_id = completed_status.id

        self.db.commit()

        return impact_eval

    def get_department_plans(self, department_id: int) -> List[Dict[str, Any]]:
        """
        Get all improvement plans for a specific department.
        """

        plans = (
            self.db.query(IAImprovePlan)
            .filter(IAImprovePlan.department_id == department_id)
            .all()
        )

        result = []
        for plan in plans:
            result.append(
                {
                    "id": plan.id,
                    "department_id": plan.department_id,
                    "status": plan.status.name if plan.status else None,
                    "created_at": (
                        plan.created_at.isoformat() if plan.created_at else None
                    ),
                    "action": (
                        plan.action_department.action.name
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                    "description": (
                        plan.action_department.action.description
                        if plan.action_department and plan.action_department.action
                        else None
                    ),
                }
            )

        return result
