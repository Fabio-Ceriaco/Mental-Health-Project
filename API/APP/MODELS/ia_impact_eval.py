from sqlalchemy import Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class IAImpactEval(Base):

    __tablename__ = "ia_impact_eval"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ia_improve_plan.id"), nullable=False
    )
    before_index: Mapped[float] = mapped_column(Float, nullable=False)
    after_index: Mapped[float] = mapped_column(Float, nullable=False)
    evaluation_date: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )

    # Relationship to Improve Plan
    improve_plan = relationship("IAImprovePlan", back_populates="impact_evaluation")
