from sqlalchemy import Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class DepartmentMetric(Base):

    __tablename__ = "department_metric"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=False
    )
    anxiety_avg: Mapped[float] = mapped_column(Float, nullable=False)
    depression_avg: Mapped[float] = mapped_column(Float, nullable=False)
    stress_avg: Mapped[float] = mapped_column(Float, nullable=False)
    burnout_avg: Mapped[float] = mapped_column(Float, nullable=False)
    percentile_25: Mapped[float] = mapped_column(Float, nullable=False)
    percentile_50: Mapped[float] = mapped_column(Float, nullable=False)
    percentile_75: Mapped[float] = mapped_column(Float, nullable=False)
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("status.id"), nullable=False
    )
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
    department = relationship("Department", back_populates="metric")
    status = relationship("Status", back_populates="department_metric")
