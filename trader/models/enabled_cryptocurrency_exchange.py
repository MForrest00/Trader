from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledCryptocurrencyExchange(Base):
    __tablename__ = "enabled_cryptocurrency_exchange"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    history = relationship(
        "EnabledCryptocurrencyExchangeHistory",
        lazy=False,
        order_by="desc(EnabledCryptocurrencyExchangeHistory.date_created)",
        backref=backref(__tablename__, lazy=False),
    )


class EnabledCryptocurrencyExchangeHistory(Base):
    __tablename__ = "enabled_cryptocurrency_exchange_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enabled_cryptocurrency_exchange_id = Column(
        Integer, ForeignKey("enabled_cryptocurrency_exchange.id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    priority = Column(SmallInteger, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
