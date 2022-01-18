from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from trader.models.base import Base


class SellSignal(Base):
    __tablename__ = "sell_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exit_implementation_run_id = Column(Integer, ForeignKey("exit_implementation_run.id"), nullable=False)
    signal_date = Column(DateTime(timezone=True), nullable=False)
    strength = Column(Numeric, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("exit_implementation_run_id", "signal_date"),)
