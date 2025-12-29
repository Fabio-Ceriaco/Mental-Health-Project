# System
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from APP.CORE.security import get_current_user, require_role
from APP.DATABASE.db_conn import get_db
from typing import Optional, Dict

# Services
from APP.SERVICES.employee_service import EmployeeService
from APP.SERVICES.user_service import UserService

# from APP.SERVICES.dashboard_service import DashboardService

# Schemas
from APP.SCHEMAS.user_schema import UserBase, UserCreate, UserResponse
from APP.SCHEMAS.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeResponse

# Repositories
# from APP.REPOSITORIES.dashboard_repository import DashboardRepository

# Models

# =================== Admin Router ===================#
# Only accessible by users with the "Admin" role
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_user), Depends(require_role("Admin"))],
)


# =================== Create Employee Endpoint ===================#


@router.post("/create-employee")
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


# =================== Update Employee Endpoint ===================#


@router.put("/update-employee/{employee_id}")
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


@router.delete("/delete-employee/{employee_id}")
def delete_employees(employee_id: int, db_session: Session = Depends(get_db)):
    """Delete an employee from the system."""

    employee_service = EmployeeService(db_session)

    db_employee = employee_service.get_employee(employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    deleted_employee = employee_service.delete_employee(employee_id)
    return deleted_employee


# =================== Register User Endpoint ===================#


@router.post("/create-user", response_model=UserBase)
def register_user(
    user_data: UserCreate, db_session: Session = Depends(get_db)
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
    return {"message": "Utilizador criado com sucesso. ", "user": user["user"]}


# =================== Delete User Endpoint ===================#


@router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db_session: Session = Depends(get_db)) -> Dict[str, str]:
    """Delete a user from the system."""

    user_service = UserService(db_session)
    db_user = user_service.get_user(user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    deleted_user = user_service.delete_user(user_id)
    if deleted_user is None:
        return {"detail": "User deleted successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user.",
        )
