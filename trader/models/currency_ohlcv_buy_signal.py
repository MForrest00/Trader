from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVBuySignal(Base):
    __tablename__ = "currency_ohlcv_buy_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_implementation_run_id = Column(
        Integer, ForeignKey("currency_ohlcv_implementation_run.id"), nullable=False
    )
    currency_ohlcv_id = Column(Integer, ForeignKey("currency_ohlcv.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("currency_ohlcv_implementation_run_id", "currency_ohlcv_id"),)
