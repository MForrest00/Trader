from sqlalchemy import Column, DateTime, Integer, SmallInteger, String
from sqlalchemy.sql import func
from trader.models.base import Base


class Timeframe(Base):
    __tablename__ = "timeframe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_label = Column(String, nullable=True, unique=True)
    seconds_length = Column(Integer, nullable=True)
    unit = Column(String(1), nullable=False)
    amount = Column(SmallInteger, nullable=False)
    ccxt_label = Column(String, nullable=True, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
