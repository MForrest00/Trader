from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVPull(Base):
    __tablename__ = "currency_ohlcv_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    base_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    from_inclusive = Column(DateTime, nullable=False)
    to_exclusive = Column(DateTime, nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    base_currency = relationship(
        "Currency", lazy=False, backref=backref(f"base_{__tablename__}s", lazy=True), foreign_keys=[base_currency_id]
    )
    quote_currency = relationship(
        "Currency", lazy=False, backref=backref(f"quote_{__tablename__}s", lazy=True), foreign_keys=[quote_currency_id]
    )
    currency_ohlcvs = relationship("CurrencyOHLCV", lazy=True, backref=backref(__tablename__, lazy=False))


class CurrencyOHLCV(Base):
    __tablename__ = "currency_ohlcv"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_pull_id = Column(Integer, ForeignKey("currency_ohlcv_pull.id"), nullable=False)
    data_date = Column(DateTime, nullable=False)
    open = Column(Numeric(33, 15), nullable=False)
    high = Column(Numeric(33, 15), nullable=False)
    low = Column(Numeric(33, 15), nullable=False)
    close = Column(Numeric(33, 15), nullable=False)
    volume = Column(Numeric(33, 15), nullable=False)
