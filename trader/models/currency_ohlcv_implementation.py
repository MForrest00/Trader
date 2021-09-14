from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVImplementation(Base):
    __tablename__ = "currency_ohlcv_implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_group_id = Column(Integer, ForeignKey("currency_ohlcv_group.id"), nullable=False)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcv_implementation_runs = relationship(
        "CurrencyOHLCVImplementationRun", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("currency_ohlcv_group_id", "strategy_version_instance_id"),)


class CurrencyOHLCVImplementationRun(Base):
    __tablename__ = "currency_ohlcv_implementation_run"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_implementation_id = Column(Integer, ForeignKey("currency_ohlcv_implementation.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcv_buy_signals = relationship(
        "CurrencyOHLCVBuySignal", lazy=True, backref=backref(__tablename__, lazy=False)
    )
