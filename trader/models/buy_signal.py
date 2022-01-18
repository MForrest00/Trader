from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from trader.models.base import Base


class BuySignal(Base):
    __tablename__ = "buy_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_implementation_run_id = Column(Integer, ForeignKey("entry_implementation_run.id"), nullable=False)
    signal_date = Column(DateTime(timezone=True), nullable=False)
    strength = Column(Numeric, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("entry_implementation_run_id", "signal_date"),)
