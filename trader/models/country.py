from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func
from trader.models.base import Base


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    official_name = Column(String(250), nullable=False)
    iso_alpha_2_code = Column(String(2), nullable=False, unique=True)
    iso_alpha_3_code = Column(String(3), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
