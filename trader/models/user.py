from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_demo = Column(Boolean, nullable=False, default=True)
    is_live = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    positions = relationship("Position", lazy=True, backref=backref(__tablename__, lazy=False))
