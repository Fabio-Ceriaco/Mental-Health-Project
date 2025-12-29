from sqlalchemy import Integer, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class AssessmentResult(Base):

    __tablename__ = "assessment_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id"), nullable=False
    )
    score_total: Mapped[float] = mapped_column(Float, nullable=False)
    score_percent: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("risk_level.id"), nullable=False
    )
    details_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )

    # Relationships
    employee = relationship("Employee", back_populates="assessment_result")
    risk_level = relationship("RiskLevel", back_populates="assessment_result")
