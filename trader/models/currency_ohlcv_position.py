from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVPosition(Base):
    __tablename__ = "currency_ohlcv_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    currency_ohlcv_buy_signal_id = Column(Integer, ForeignKey("currency_ohlcv_buy_signal.id"), nullable=False)
    bought_size = Column(Numeric(33, 15), nullable=False)
    data = Column(JSONB, nullable=True)
    close_currency_ohlcv_implementation_run_id = Column(
        Integer, ForeignKey("currency_ohlcv_implementation_run.id"), nullable=True
    )
    close_currency_ohlcv_id = Column(Integer, ForeignKey("currency_ohlcv.id"), nullable=True)
    date_opened = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_closed = Column(DateTime(timezone=True), nullable=True)
