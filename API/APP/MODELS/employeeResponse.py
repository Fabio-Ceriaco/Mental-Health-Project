from sqlalchemy import Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class EmployeeResponse(Base):

    __tablename__ = "employee_response"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id"), nullable=False
    )
    assessment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assessment.id"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), nullable=False
    )
    answer_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee", back_populates="response")
    assessment = relationship("Assessment", back_populates="response")
    question = relationship("Question", back_populates="response")
