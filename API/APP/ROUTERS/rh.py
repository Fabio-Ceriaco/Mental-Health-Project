# System
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from APP.CORE.security import get_current_user, require_role
from APP.DATABASE.db_conn import get_db
from typing import Any, List, Optional, Dict

# Models
from APP.MODELS.employee import Employee

# Services
from APP.SERVICES.employee_service import EmployeeService
from APP.SERVICES.dashboard_service import DashboardService
from APP.SERVICES.alert_service import AlertService

# Schemas
from APP.SCHEMAS.employee_schema import (
    EmployeeCreate,
    EmployeeBase,
    EmployeeResponse,
    EmployeeUpdate,
)

# Repositories
from APP.REPOSITORIES.dashboard_repository import DashboardRepository
from APP.REPOSITORIES.assessment_repository import AssessmentRepository

# ==================== RH Router ===================#
# Only accessible by users with the "Executive" role
router = APIRouter(
    prefix="/rh",
    tags=["RH"],
    dependencies=[
        Depends(get_current_user),
        Depends(require_role("RH", "Psychologist")),
    ],
)


# =================== Create Employee Endpoint ===================#


@router.post("/create-employee", response_model=EmployeeResponse)
def create_employees(
    employee_data: EmployeeCreate, db_session: Session = Depends(get_db)
) -> Optional[EmployeeResponse]:
    """Create a new employee in the system."""

    try:
        employee_service = EmployeeService(db_session)
        return employee_service.create_employee(employee_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No endpoint create_employee deu erro: {str(e)}",
        )


# =================== Get All Employees Endpoint ===================#


@router.get("/get-all-employees", response_model=List[EmployeeBase])
def get_all_employees(db_session: Session = Depends(get_db)) -> List[Employee]:
    """Retrieve all employees from the system."""

    try:
        employee_service = EmployeeService(db_session)
        employee: List[Employee] = employee_service.get_all()
        return employee
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =================== Update Employee Endpoint ===================#


@router.put("/update-employee/{employee_id}", response_model=EmployeeResponse)
def update_employees(
    employee_id: int,
    update_data: EmployeeUpdate,
    db_session: Session = Depends(get_db),
) -> Optional[EmployeeResponse]:
    """Update an existing employee's details."""

    try:
        employee_service = EmployeeService(db_session)
        update_employee = employee_service.update_employee(employee_id, update_data)  # type: ignore
        return update_employee
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =================== Delete Employee Endpoint ===================#


@router.delete("/delete_employee/{employee_id}")
def delete_employees(
    employee_id: int, db_session: Session = Depends(get_db)
) -> Optional[EmployeeResponse]:
    """Delete an employee from the system."""

    employee_service = EmployeeService(db_session)

    db_employee = employee_service.get_employee(employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    deleted_employee = employee_service.delete_employee(employee_id)
    return deleted_employee


# =================== Process All Employees Assessments =================#


@router.post("/process-all-assessments")
def process_all_employees_assessments(
    db_session: Session = Depends(get_db),
) -> Dict[str, Any]:

    try:
        repo = AssessmentRepository(db_session)
        results = repo.process_all_assessments()
        return {
            "message": "All employee assessments have been processed.",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =================== Global Dashboard Endpoint ===================#


@router.get("/dashboard/global")
def get_global_dashboard(db_session: Session = Depends(get_db)):
    """Endpoint to retrieve global dashboard data."""

    repo = DashboardRepository(db_session)
    service = DashboardService(repo)

    global_dashboard = service.get_global_dashboard_data()
    return global_dashboard


# =================== Alerts Summary Endpoint ===================#


@router.get("/alerts/summary")
def get_alerts_summary(db_session: Session = Depends(get_db)):
    """Return aggregated counts of alerts by type and status buckets."""

    try:
        service = AlertService(db_session)
        return service.get_summary()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/alerts")
def list_alerts(limit: int = 20, db_session: Session = Depends(get_db)):
    """Return recent alerts with type, severity, department, employee, and message."""

    try:
        service = AlertService(db_session)
        return service.list_recent(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/alerts/seed")
def seed_alerts_from_assessments(db_session: Session = Depends(get_db)):
    """Seed alert types and generate alerts for all employees based on past assessments."""

    try:
        service = AlertService(db_session)
        seeded_types = service.seed_alert_types_default()
        generated = service.generate_alerts_from_assessments()
        return {"alert_types": seeded_types, "alerts": generated}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/assessments")
def list_all_assessments(db_session: Session = Depends(get_db)):
    """List all employee assessments with scores and risk levels."""

    try:
        repo = AssessmentRepository(db_session)
        results = repo.get_all_assessments_with_details()
        return {"items": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =================== IA Improve Plans Endpoints ===================#


@router.get("/ia-plans")
def get_all_ia_plans(db_session: Session = Depends(get_db)):
    """Get all IA improvement plans."""
    from APP.REPOSITORIES.ia_plan_repository import IAPlanRepository

    try:
        repo = IAPlanRepository(db_session)
        plans = repo.get_all_plans()
        return {"items": plans, "total": len(plans)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ia-plans/{plan_id}")
def get_ia_plan(plan_id: int, db_session: Session = Depends(get_db)):
    """Get a specific IA improvement plan by ID."""
    from APP.REPOSITORIES.ia_plan_repository import IAPlanRepository

    try:
        repo = IAPlanRepository(db_session)
        plan = repo.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ia-plans/department/{department_id}")
def get_ia_plans_by_department(
    department_id: int, db_session: Session = Depends(get_db)
):
    """Get all IA improvement plans for a specific department."""
    from APP.REPOSITORIES.ia_plan_repository import IAPlanRepository

    try:
        repo = IAPlanRepository(db_session)
        plans = repo.get_plans_by_department(department_id)
        return {"items": plans, "total": len(plans)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/ia-plans/{plan_id}/status")
def update_ia_plan_status(
    plan_id: int, status_id: int, db_session: Session = Depends(get_db)
):
    """Update the status of an IA improvement plan."""
    from APP.REPOSITORIES.ia_plan_repository import IAPlanRepository

    try:
        repo = IAPlanRepository(db_session)
        updated_plan = repo.update_plan_status(plan_id, status_id)
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )
        return updated_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/ia-plans/{plan_id}/impact")
def create_impact_evaluation(
    plan_id: int,
    before_index: float,
    after_index: float,
    db_session: Session = Depends(get_db),
):
    """Create an impact evaluation for an IA improvement plan."""
    from APP.REPOSITORIES.ia_plan_repository import IAPlanRepository

    try:
        repo = IAPlanRepository(db_session)
        impact = repo.create_impact_evaluation(plan_id, before_index, after_index)
        if not impact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )
        return impact
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =================== AI Improvement Plan Generation ===================#


@router.post("/ai-generate-plans")
def generate_ai_improvement_plans(
    threshold: float | None = None,
    dry_run: bool | None = False,
    db_session: Session = Depends(get_db),
):
    """
    Check all departments for metrics exceeding 60% threshold
    and automatically generate AI improvement plans.
    """
    from APP.SERVICES.ai_improvement_service import AIImprovementService

    try:
        ai_service = AIImprovementService(db_session)
        results = ai_service.check_and_generate_plans(threshold, bool(dry_run))
        return {
            "success": True,
            "message": f"Checked {results['checked_departments']} departments, generated {results['plans_generated']} new improvement plans",
            "data": results,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/ai-evaluate-impact/{plan_id}")
def evaluate_plan_impact(
    plan_id: int,
    before_index: float,
    after_index: float,
    db_session: Session = Depends(get_db),
):
    """
    Evaluate the impact of an implemented improvement plan
    by comparing before and after metrics.
    """
    from APP.SERVICES.ai_improvement_service import AIImprovementService

    try:
        ai_service = AIImprovementService(db_session)
        evaluation = ai_service.evaluate_plan_impact(plan_id, before_index, after_index)

        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found or evaluation failed",
            )

        improvement = ((after_index - before_index) / before_index) * 100

        return {
            "success": True,
            "evaluation": {
                "id": evaluation.id,
                "plan_id": evaluation.plan_id,
                "before_index": evaluation.before_index,
                "after_index": evaluation.after_index,
                "improvement_percentage": improvement,
                "evaluation_date": evaluation.evaluation_date.isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ai-plans-by-department/{department_id}")
def get_department_ai_plans(department_id: int, db_session: Session = Depends(get_db)):
    """Get all AI improvement plans for a specific department."""
    from APP.SERVICES.ai_improvement_service import AIImprovementService

    try:
        ai_service = AIImprovementService(db_session)
        plans = ai_service.get_department_plans(department_id)
        return {"items": plans, "total": len(plans)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
