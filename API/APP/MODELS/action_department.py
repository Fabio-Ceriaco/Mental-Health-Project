from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class ActionDepartment(Base):

    __tablename__ = "action_department"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("action.id"), nullable=False
    )
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=False
    )
    date_assigned: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship with Action and Department
    action = relationship("Action", back_populates="department")
    department = relationship("Department", back_populates="action")
    improve_plan = relationship("IAImprovePlan", back_populates="action_department")
