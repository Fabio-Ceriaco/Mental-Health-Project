# System
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Any, Dict, List

# Auth / DB
from APP.CORE.security import get_current_user, require_role
from APP.DATABASE.db_conn import get_db

# Models
from APP.MODELS.user import User

# Services / Repos
from APP.SERVICES.alert_service import AlertService
from APP.REPOSITORIES.assessment_repository import AssessmentRepository


# ==================== Psychologist Router ===================#
# Accessible by users with the "Psychologist" role
router = APIRouter(
    prefix="/psychologist",
    tags=["Psychologist"],
    dependencies=[Depends(get_current_user), Depends(require_role("Psychologist"))],
)


@router.get("/assessments")
def list_all_assessments(db_session: Session = Depends(get_db)) -> Dict[str, Any]:
    """List all employee assessments with scores and risk levels."""

    try:
        repo = AssessmentRepository(db_session)
        results = repo.get_all_assessments_with_details()
        return {"items": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/alerts/recent")
def list_recent_alerts(limit: int = 20, db_session: Session = Depends(get_db)):
    """List recent alerts (read-only) for psychologists."""

    try:
        service = AlertService(db_session)
        return service.list_recent(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/interventions")
def list_all_interventions(db_session: Session = Depends(get_db)) -> Dict[str, Any]:
    """List all active psychologist interventions with employee and action details."""
    from APP.MODELS.psychologist_interv import PsychologistInterv
    from APP.MODELS.employee import Employee
    from APP.MODELS.interventions_actions import InterventionAction
    from APP.MODELS.action import Action

    try:
        results = (
            db_session.query(
                PsychologistInterv.id,
                PsychologistInterv.employee_id,
                Employee.name,
                PsychologistInterv.description,
                PsychologistInterv.created_at,
                PsychologistInterv.updated_at,
                Action.name.label("action_name"),
            )
            .join(Employee, PsychologistInterv.employee_id == Employee.id)
            .join(
                InterventionAction,
                PsychologistInterv.intervention_action_id == InterventionAction.id,
            )
            .join(Action, InterventionAction.action_id == Action.id)
            .all()
        )

        items = [
            {
                "id": r.id,
                "employee_id": r.employee_id,
                "employee_name": r.name,
                "intervention_action_name": r.action_name,
                "description": r.description,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in results
        ]

        return {"items": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class InterventionCreate(BaseModel):
    employee_id: int
    description: str
    intervention_action_id: int | None = None


@router.post("/interventions")
def create_intervention(
    payload: InterventionCreate, db_session: Session = Depends(get_db)
) -> Dict[str, Any]:
    from APP.MODELS.psychologist_interv import PsychologistInterv
    from APP.MODELS.employee import Employee
    from APP.MODELS.interventions_actions import InterventionAction
    from APP.MODELS.action import Action

    # Validate employee
    employee = (
        db_session.query(Employee).filter(Employee.id == payload.employee_id).first()
    )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    # Resolve intervention_action_id
    intervention_action_id = payload.intervention_action_id
    if intervention_action_id:
        ia = (
            db_session.query(InterventionAction)
            .filter(InterventionAction.id == intervention_action_id)
            .first()
        )
        if not ia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intervention action not found",
            )
    else:
        ia = (
            db_session.query(InterventionAction)
            .order_by(InterventionAction.id.asc())
            .first()
        )
        if not ia:
            # Create a fallback action/intervention_action if none exist
            action = Action(
                name="Intervenção Manual",
                description="Criada automaticamente",
                start_date=datetime.utcnow(),
                end_date=None,
                is_active=True,
            )
            db_session.add(action)
            db_session.flush()

            ia = InterventionAction(action_id=action.id)
            db_session.add(ia)
            db_session.flush()
        intervention_action_id = ia.id

    interv = PsychologistInterv(
        employee_id=payload.employee_id,
        intervention_action_id=intervention_action_id,
        description=payload.description,
    )
    db_session.add(interv)
    db_session.commit()
    db_session.refresh(interv)

    # Return minimal representation
    action_name = None
    if ia and ia.action:
        action_name = ia.action.name

    return {
        "id": interv.id,
        "employee_id": interv.employee_id,
        "description": interv.description,
        "intervention_action_id": intervention_action_id,
        "intervention_action_name": action_name,
        "created_at": interv.created_at,
        "updated_at": interv.updated_at,
    }


@router.delete("/interventions/{intervention_id}")
def delete_intervention(
    intervention_id: int, db_session: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Delete a specific psychologist intervention by id."""
    from APP.MODELS.psychologist_interv import PsychologistInterv

    try:
        interv = (
            db_session.query(PsychologistInterv)
            .filter(PsychologistInterv.id == intervention_id)
            .first()
        )
        if not interv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found"
            )

        db_session.delete(interv)
        db_session.commit()
        return {"success": True, "id": intervention_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class InterventionUpdate(BaseModel):
    description: str


@router.patch("/interventions/{intervention_id}")
def update_intervention(
    intervention_id: int,
    payload: InterventionUpdate,
    db_session: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Update a psychologist intervention description."""
    from APP.MODELS.psychologist_interv import PsychologistInterv
    from APP.MODELS.interventions_actions import InterventionAction

    try:
        interv = (
            db_session.query(PsychologistInterv)
            .filter(PsychologistInterv.id == intervention_id)
            .first()
        )
        if not interv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found"
            )

        interv.description = payload.description
        db_session.commit()
        db_session.refresh(interv)

        # Fetch related action name for response
        ia = (
            db_session.query(InterventionAction)
            .filter(InterventionAction.id == interv.intervention_action_id)
            .first()
        )
        action_name = ia.action.name if ia and ia.action else None

        return {
            "id": interv.id,
            "employee_id": interv.employee_id,
            "description": interv.description,
            "intervention_action_id": interv.intervention_action_id,
            "intervention_action_name": action_name,
            "created_at": interv.created_at,
            "updated_at": interv.updated_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
