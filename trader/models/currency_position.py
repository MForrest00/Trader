from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyPosition(Base):
    __tablename__ = "currency_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    open_implementation_run_step_id = Column(Integer, ForeignKey("implementation_run_step.id"), nullable=False)
    open_currency_ohlcv_id = Column(Integer, ForeignKey("currency_ohlcv.id"), nullable=False)
    open_dataframe_row_index = Column(Integer, nullable=False)
    bought_size = Column(Numeric(33, 15), nullable=False)
    bought_price = Column(Numeric(33, 15), nullable=False)
    data = Column(JSONB, nullable=True)
    close_implementation_run_step_id = Column(Integer, ForeignKey("implementation_run_step.id"), nullable=True)
    close_currency_ohlcv_id = Column(Integer, ForeignKey("currency_ohlcv.id"), nullable=True)
    close_dataframe_row_index = Column(Integer, nullable=True)
    sold_price = Column(Numeric(33, 15), nullable=True)
    date_opened = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_closed = Column(DateTime(timezone=True), nullable=True)

    # Many to one
    open_currency_ohlcv = relationship(
        "CurrencyOHLCV",
        lazy=False,
        backref=backref(f"open_{__tablename__}s", lazy=True),
        foreign_keys=[open_currency_ohlcv_id],
    )
    quote_currency = relationship(
        "CurrencyOHLCV",
        lazy=False,
        backref=backref(f"close_{__tablename__}s", lazy=True),
        foreign_keys=[close_currency_ohlcv_id],
    )
