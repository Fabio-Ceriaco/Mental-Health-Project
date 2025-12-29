from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class Alert(Base):

    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alert_type.id"), nullable=False
    )
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id"), nullable=True
    )
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship with AlertType
    alert_type = relationship("AlertType", back_populates="alert")
    department = relationship("Department", back_populates="alert")
    employee = relationship("Employee", back_populates="alert")
