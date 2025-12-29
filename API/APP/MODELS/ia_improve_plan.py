from sqlalchemy import Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class IAImprovePlan(Base):

    __tablename__ = "ia_improve_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=False
    )
    action_department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("action_department.id"), nullable=False
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("status.id"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    department = relationship("Department", back_populates="improve_plan")
    action_department = relationship("ActionDepartment", back_populates="improve_plan")
    status = relationship("Status", back_populates="ia_improve_plan")
    impact_evaluation = relationship("IAImpactEval", back_populates="improve_plan")
