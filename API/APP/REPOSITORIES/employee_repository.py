# System
from sqlalchemy.orm import Session, defer
from typing import Any, Dict, List, Optional

# Models
from APP.MODELS.role import Role
from APP.MODELS import Employee
from APP.MODELS.gender import Gender
from APP.MODELS.marital_status import MaritalStatus

# Schemas
from APP.SCHEMAS.employee_schema import (
    EmployeeProfileOptionsResponse,
    OptionItem,
    EmployeeBase,
)

# Repositories
from APP.REPOSITORIES.base_repository import BaseRepository


class EmployeeRepository(BaseRepository):

    def __init__(self, db_session: Session):
        super().__init__(db_session, Employee)

    # =================== CRUD Operations ===================#

    def get(self, employee_id: int) -> Optional[Employee]:
        return (
            self.db_session.query(Employee).filter(Employee.id == employee_id).first()
        )

    def get_employee_by_email(self, email: str) -> Optional[EmployeeBase]:
        row = (
            self.db_session.query(Employee, Role.name.label("role_name"))
            .outerjoin(Role, Role.id == Employee.role_id)
            .filter(Employee.email == email)
            .first()
        )
        if not row:
            return None
        employee, role_name = row
        employee_dict: Dict[Any, Any] = {**employee.__dict__, "role_name": role_name}
        return EmployeeBase.model_validate(employee_dict)

    def list(self, skip: int = 0, limit: int | None = None) -> List[Employee]:
        query = self.db_session.query(Employee).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_employee_profile(self, employee_id: int):

        row = (
            self.db_session.query(
                Employee.id,
                Employee.name,
                Employee.phone_number,
                Employee.gender_id,
                Gender.name.label("gender_label"),
                Employee.date_of_birth,
                Employee.zip_code,
                Employee.location,
                Employee.marital_status_id,
                MaritalStatus.name.label("marital_status_label"),
                Employee.num_children,
                Employee.role_id,
                Role.name.label("role_label"),
            )
            .outerjoin(Gender, Gender.id == Employee.gender_id)
            .outerjoin(MaritalStatus, MaritalStatus.id == Employee.marital_status_id)
            .filter(Employee.id == employee_id)
            .first()
        )

        if not row:
            return None

        return dict(row._mapping)

    def get_profile_options(self) -> EmployeeProfileOptionsResponse:

        genders = (
            self.db_session.query(Gender, Gender.name.label("label"))
            .order_by(Gender.id)
            .all()
        )

        marital_status = (
            self.db_session.query(MaritalStatus, MaritalStatus.name.label("label"))
            .order_by(MaritalStatus.id)
            .all()
        )
        role = (
            self.db_session.query(Role, Role.name.label("label"))
            .order_by(Role.id)
            .all()
        )

        return EmployeeProfileOptionsResponse(
            genders=[OptionItem(id=g.id, label=g.name) for g, _ in genders],
            marital_status=[
                OptionItem(id=ms.id, label=ms.name) for ms, _ in marital_status
            ],
            role=[OptionItem(id=r.id, label=r.name) for r, _ in role],
        )
