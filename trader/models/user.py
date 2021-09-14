from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from trader.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_live = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
