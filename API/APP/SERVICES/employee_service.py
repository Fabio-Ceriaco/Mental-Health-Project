from typing import Any, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from APP.MODELS.employee import Employee
from APP.REPOSITORIES.employee_repository import EmployeeRepository
from APP.SCHEMAS.employee_schema import (
    EmployeeBase,
    EmployeeUpdate,
    EmployeeCreate,
    EmployeeProfileOptionsResponse,
)


class EmployeeService:

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.repo = EmployeeRepository(db_session)

    """Service for managing Employee operations."""

    def create_employee(self, employee: EmployeeCreate) -> Employee:
        """Create a new employee after checking for email uniqueness."""

        existing_employee = self.repo.get_employee_by_email(employee.email)
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email já está em uso."
            )

        db_employee = Employee(**employee.model_dump())
        return self.repo.create(db_employee)

    def get_employee(self, employee_id: int) -> Employee | None:
        """Retrieve an employee by their ID."""

        return self.repo.get(employee_id)

    def get_employee_profile(self, employee_id: int) -> Any:
        """Retrieve an employee's profile by their ID."""

        return self.repo.get_employee_profile(employee_id)

    def get_employee_profile_options(self) -> EmployeeProfileOptionsResponse:
        """Retrieve options for employee profile fields."""

        return self.repo.get_profile_options()

    def get_employee_by_email(self, email: str) -> EmployeeBase | None:
        """Retrieve an employee by their email."""

        return self.repo.get_employee_by_email(email)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        """Retrieve all employees."""
        if not self.repo.list():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No employees found."
            )
        return self.repo.list(skip=skip, limit=limit)

    def update_employee(self, employee_id: int, employee: EmployeeUpdate) -> Employee:
        """Update an existing employee's details."""

        db_employee = self.repo.get(employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        update_data = employee.model_dump(exclude_unset=True)
        updated_employee = self.repo.update(db_employee, update_data)
        return updated_employee

    def delete_employee(self, employee_id: int):
        """Delete an employee by their ID."""

        db_employee = self.repo.get(employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found."
            )
        deleted_employee = self.repo.delete(db_employee)
        return deleted_employee
