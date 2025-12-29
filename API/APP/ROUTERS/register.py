# System
from typing import Dict
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from APP.DATABASE.db_conn import get_db


# Services
from APP.SERVICES.user_service import UserService
from APP.SERVICES.employee_service import EmployeeService

# Schemas
from APP.SCHEMAS.user_schema import UserCreate, UserResponse

# Repositories


# Models


router = APIRouter(prefix="/register", tags=["Registration"])  # Registration router


@router.post(
    "/",
)
def register_user(
    user_data: UserCreate,
    db_session: Session = Depends(get_db),
) -> Dict[str, str | UserResponse]:
    """Register a new user in the system."""

    user_service = UserService(db_session)
    employee = EmployeeService(db_session)

    employee = employee.get_employee_by_email(user_data.email)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Funcionário não encontrado para o email fornecido.",
        )

    if user_service.has_user_for_employee(employee.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este funcionário já tem uma conta associada.",
        )

    user = user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        employee_id=employee.id,
    )
    if user:
        return {"message": "Utilizador criado com sucesso."}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro ao criar o utilizador.",
    )
