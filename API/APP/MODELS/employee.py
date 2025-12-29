from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class Employee(Base):

    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    gender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("gender.id"), nullable=True
    )
    date_of_birth: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    marital_status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("marital_status.id"), nullable=True
    )
    num_children: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    hire_date: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    contract_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract_type.id"), nullable=True
    )
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships with other models
    gender = relationship("Gender", back_populates="employee")
    marital_status = relationship("MaritalStatus", back_populates="employee")
    contract_type = relationship("ContractType", back_populates="employee")
    department = relationship("Department", back_populates="employee")
    role = relationship("Role", back_populates="employee", lazy="joined")
    user = relationship("User", back_populates="employee", uselist=False)
    intervention = relationship("PsychologistInterv", back_populates="employee")
    response = relationship("EmployeeResponse", back_populates="employee")
    alert = relationship("Alert", back_populates="employee")
    assessment_result = relationship("AssessmentResult", back_populates="employee")

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None
