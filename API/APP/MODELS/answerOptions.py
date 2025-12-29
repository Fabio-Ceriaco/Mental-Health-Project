from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from APP.DATABASE.db_conn import Base


class AnswerOption(Base):

    __tablename__ = "answer_option"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
