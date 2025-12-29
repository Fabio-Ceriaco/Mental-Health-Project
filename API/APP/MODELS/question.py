from sqlalchemy import Integer, String, Text, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class Question(Base):

    __tablename__ = "question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    dimension: Mapped[str] = mapped_column(String, nullable=False)
    is_inverted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=0
    )  # 0 for False, 1 for True

    # Relationship to EmployeeResponse

    response = relationship("EmployeeResponse", back_populates="question")
