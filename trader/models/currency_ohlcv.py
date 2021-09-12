from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVGroup(Base):
    __tablename__ = "currency_ohlcv_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    base_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcv_pulls = relationship("CurrencyOHLCVPull", lazy=True, backref=backref(__tablename__, lazy=False))

    # Many to one
    base_currency = relationship(
        "Currency", lazy=False, backref=backref(f"base_{__tablename__}s", lazy=True), foreign_keys=[base_currency_id]
    )
    quote_currency = relationship(
        "Currency", lazy=False, backref=backref(f"quote_{__tablename__}s", lazy=True), foreign_keys=[quote_currency_id]
    )

    __table_args__ = (UniqueConstraint("source_id", "base_currency_id", "quote_currency_id", "timeframe_id"),)


class CurrencyOHLCVPull(Base):
    __tablename__ = "currency_ohlcv_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_group_id = Column(Integer, ForeignKey("currency_ohlcv_group.id"), nullable=False)
    from_inclusive = Column(DateTime(timezone=True), nullable=False)
    to_exclusive = Column(DateTime(timezone=True), nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcvs = relationship("CurrencyOHLCV", lazy=True, backref=backref(__tablename__, lazy=False))


class CurrencyOHLCV(Base):
    __tablename__ = "currency_ohlcv"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_pull_id = Column(Integer, ForeignKey("currency_ohlcv_pull.id"), nullable=False)
    date_open = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(33, 15), nullable=False)
    high = Column(Numeric(33, 15), nullable=False)
    low = Column(Numeric(33, 15), nullable=False)
    close = Column(Numeric(33, 15), nullable=False)
    volume = Column(Numeric(33, 15), nullable=False)
    date_high = Column(DateTime(timezone=True), nullable=True)
    date_low = Column(DateTime(timezone=True), nullable=True)
