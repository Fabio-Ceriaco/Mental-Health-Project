from sqlalchemy import ForeignKey, Integer, DateTime, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class PsychologistInterv(Base):

    __tablename__ = "psychologist_interv"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id"), nullable=False
    )
    intervention_action_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("intervention_action.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
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
    employee = relationship("Employee", back_populates="intervention")
    intervention_action = relationship(
        "InterventionAction", back_populates="psychologist_intervention"
    )
