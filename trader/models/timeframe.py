from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.sql import func
from trader.models.base import Base


class Timeframe(Base):
    __tablename__ = "timeframe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_label = Column(String(5), nullable=True, unique=True)
    seconds_length = Column(Integer, nullable=True)
    ccxt_label = Column(String(3), nullable=True, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
