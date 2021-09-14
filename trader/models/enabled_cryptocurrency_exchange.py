from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledCryptocurrencyExchange(Base):
    __tablename__ = "enabled_cryptocurrency_exchange"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False, unique=True)
    priority = Column(SmallInteger, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)
    date_enabled = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
