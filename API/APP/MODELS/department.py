from sqlalchemy import Integer, DateTime, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class Department(Base):

    __tablename__ = "department"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
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
    alert = relationship("Alert", back_populates="department")
    improve_plan = relationship("IAImprovePlan", back_populates="department")
    employee = relationship("Employee", back_populates="department")
    metric = relationship("DepartmentMetric", back_populates="department")
    action = relationship("ActionDepartment", back_populates="department")
