# System
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from APP.DATABASE.db_conn import get_db
from fastapi.security import OAuth2PasswordRequestForm

# Services
from APP.SERVICES.auth_service import AuthenticationService
from APP.SERVICES.user_service import UserService
from APP.SERVICES.employee_service import EmployeeService

# Schemas
from APP.SCHEMAS.employee_schema import EmployeeBase
from APP.SCHEMAS.auth_schema import TokenDataSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])  # Authentication router


@router.post("/login", response_model=TokenDataSchema)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db),
) -> dict[str, str | dict[str, int] | EmployeeBase]:
    """Authenticate a user and provide an access token."""
    user_service = UserService(db_session)
    employee_service = EmployeeService(db_session)

    try:
        auth_service = AuthenticationService(db_session)
        token = auth_service.authenticate_user(
            form_data.username, form_data.password
        )  # Authenticate user

        user = user_service.get_user_by_email(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        employee = employee_service.get_employee_by_email(form_data.username)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found."
            )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
            "employee": employee,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
