# System
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List
from APP.DATABASE.db_conn import get_db
from APP.CORE.security import get_current_user, require_role

# Models
from APP.MODELS.user import User

# Services
from APP.SERVICES.user_service import UserService
from APP.SERVICES.employee_service import EmployeeService
from APP.SERVICES.dashboard_service import DashboardService
from APP.SERVICES.assessment_service import QuestionInput
from APP.SERVICES.assessment_service import calculate_assessment
from APP.SERVICES.alert_service import AlertService
from APP.ml.ml_service import PredictService
from APP.ml.dataset_builder import build_dataset

# Schemas
from APP.SCHEMAS.employee_schema import (
    EmployeeBase,
    EmployeeUpdate,
    EmployeeProfileResponse,
    EmployeeProfileOptionsResponse,
)
from APP.SCHEMAS.dashboard_schema import EmployeeDashboard
from APP.SCHEMAS.assessment_schema import AssessmentOutput, SubmitAssessment

# Repositories
from APP.REPOSITORIES.question_repository import QuestionRepository
from APP.REPOSITORIES.dashboard_repository import DashboardRepository
from APP.REPOSITORIES.assessment_repository import AssessmentRepository

# ==================== Employee Router ===================#
# Only accessible by users with the "User" role
router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    dependencies=[Depends(get_current_user), Depends(require_role("User"))],
)

# Cache feature order for ML predictions to avoid recomputing
FEATURE_ORDER_CACHE: list[str] | None = None


# =================== Get Employee Profile Endpoint ===================#


@router.get("/profile", response_model=EmployeeProfileResponse)
def get_employee_profile(
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the profile of the authenticated employee."""
    print("Current User:", current_user)

    employee_service = EmployeeService(db_session)

    profile = employee_service.get_employee_profile(current_user.employee_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil do funcionário não encontrado.",
        )

    return profile


@router.get("/profile/options", response_model=EmployeeProfileOptionsResponse)
def get_employee_profile_options(
    db_session: Session = Depends(get_db),
):
    """Retrieve options for employee profile."""

    employee_service = EmployeeService(db_session)

    options = employee_service.repo.get_profile_options()

    return options


# =================== Update Employee Profile Endpoint ===================#


@router.patch("/profile", response_model=dict[str, EmployeeBase])
def update_employee_profile(
    employee_update: EmployeeUpdate,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, EmployeeBase]:
    """Update the profile of the authenticated employee."""

    try:
        employee_service = EmployeeService(db_session)
        employee = employee_service.get_employee(current_user.employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Funcionário não encontrado.",
            )
        updated_employee = employee_service.update_employee(
            current_user.employee_id,
            EmployeeUpdate(**employee_update.model_dump(exclude_unset=True)),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar o perfil: {str(e)}",
        )

    return {"employee": updated_employee}


# =================== Delete Employee Profile Endpoint ===================#


@router.delete("/profile", response_model=dict[str, Any])
def delete_employee_profile(
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Delete the profile of the authenticated employee."""

    user_service = UserService(db_session)
    employee_service = EmployeeService(db_session)

    try:
        email = current_user.email
        employee = employee_service.get_employee_by_email(email)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Funcionário não encontrado.",
            )

        employee_service.delete_employee(employee.id)
        user_service.delete_user(current_user.id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar o perfil: {str(e)}",
        )

    return {"message": "Perfil do funcionário deletado com sucesso."}


# =================== Get Assessments for Employee Endpoint ===================#


@router.get("/assessments/templates")
def get_template_for_employee(
    db_session: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve assessment templates for the authenticated employee."""

    qrepo = QuestionRepository(db_session)

    questions = qrepo.get_questions(limit=40)

    return {
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "options": [
                    {"label": "Nunca", "value": 0},
                    {"label": "Raramente", "value": 1},
                    {"label": "Às vezes", "value": 2},
                    {"label": "Frequentemente", "value": 3},
                    {"label": "Sempre", "value": 4},
                ],
            }
            for q in questions
        ]
    }

    # return {"template_id": assessment_id,
    #     "questions": [{"id": q.question_id, "text": q.text, "options": [{"label": "Nunca", "value": 0}, \
    #     {"label": "Raramente", "value": 1}, {"label": "Às vezes", "value": 2},\
    #     {"label": "Frequentemente", "value": 3}, {"label": "Sempre", "value": 4}]} for q in questions]}


# ==================== Submit Assessment Endpoint ===================#


@router.post("/assessments/submit", response_model=AssessmentOutput)
def submit_assessment(
    payload: SubmitAssessment,
    db_session: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Submit an assessment for the authenticated employee."""

    if not payload.responses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As respostas do questionário não podem estar vazias.",
        )

    assess_repo = AssessmentRepository(db_session)
    # Get ansswered question IDs
    q_ids = [resp.question_id for resp in payload.responses]
    question_map = assess_repo.load_questions_by_ids(q_ids)

    # Check for missing questions
    missing = [qid for qid in q_ids if qid not in question_map]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Perguntas inválidas: {missing}",
        )

    # Prepare inputs for assessment calculation
    q_inputs: List[QuestionInput] = []
    for resp in payload.responses:
        question = question_map[resp.question_id]
        if resp.answer_value < 0 or resp.answer_value > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Valor de resposta inválido para a pergunta {resp.question_id}. Deve estar entre 0 e 4.",
            )

        qi = QuestionInput(
            id=resp.question_id,
            weight=float(question.weight),
            dimension=question.dimension,
            is_inverted=bool(question.is_inverted),
            answer_value=int(resp.answer_value),
        )
        q_inputs.append(qi)

    # Calculate assessment result
    calc_result = calculate_assessment(q_inputs)

    # Persist responses and result
    # Convert responses to dicts
    resp_dicts = [
        {
            "assessment_id": payload.assessment_id,
            "question_id": r.question_id,
            "answer_value": r.answer_value,
        }
        for r in payload.responses
    ]
    assess_repo.save_employee_responses(
        payload.employee_id, payload.assessment_id, resp_dicts
    )
    assess_repo.save_assessment_result(
        payload.employee_id, payload.assessment_id, calc_result
    )

    # Load employee once for downstream alerts
    employee_service = EmployeeService(db_session)
    employee = None
    try:
        employee = employee_service.get_employee(payload.employee_id)
    except Exception:
        employee = None

    # Harassment alerts only when "Sempre" on assédio questions
    try:
        if employee:
            alert_service = AlertService(db_session)
            alert_service.create_harassment_alerts_from_responses(
                employee=employee,
                responses=payload.responses,
                question_map=question_map,
            )
    except Exception as e:
        print(f"[submit_assessment] Harassment alert generation failed: {e}")

    # Trigger prediction and alert creation (best-effort)
    try:
        global FEATURE_ORDER_CACHE
        if not FEATURE_ORDER_CACHE:
            X, y, _df = build_dataset(db_session)
            FEATURE_ORDER_CACHE = X.columns.tolist() if not X.empty else []

        if FEATURE_ORDER_CACHE and employee:
            ml_service = PredictService(db_session)
            pred = ml_service.predict_employee(payload.employee_id, FEATURE_ORDER_CACHE)
            prediction = pred.get("prediction", {}) if isinstance(pred, dict) else {}
            predicted_level = int(prediction.get("predicted_risk_level", 0))
            risk_label = prediction.get("risk_label", f"Risk Level {predicted_level}")

            alert_service = AlertService(db_session)
            alert_service.create_from_prediction(
                employee=employee,
                predicted_level=predicted_level,
                risk_label=risk_label,
                score_percent=calc_result.get("score_percent", 0.0),
            )
    except Exception as e:
        # Do not block assessment submission if prediction/alert fails
        print(f"[submit_assessment] Prediction/alert failed: {e}")

    # Prepare output
    output: Dict[str, Any] = {
        "employee_id": payload.employee_id,
        "score_total": calc_result["score_total"],
        "score_max": calc_result["score_max"],
        "score_percent": calc_result["score_percent"],
        "risk_level": calc_result["risk_level"],
        "per_dimension": calc_result["per_dimension"],
        "question_breakdown": calc_result["question_breakdown"],
    }
    return output


# ==================== Get Employee Dashboard Endpoint ===================#


@router.get("/dashboard/{employee_id}", response_model=EmployeeDashboard)
def get_employee_dashboard(
    employee_id: int,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrieve dashboard data for the authenticated employee."""

    # Security: Ensure the employee can only access their own dashboard
    if current_user.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own dashboard.",
        )

    repo = DashboardRepository(db_session)
    service = DashboardService(repo)

    try:
        dashboard_data = service.get_employee_dashboard(employee_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return dashboard_data
