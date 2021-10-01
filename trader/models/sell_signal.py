from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class SellSignal(Base):
    __tablename__ = "sell_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    implementation_run_id = Column(Integer, ForeignKey("implementation_run.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    signal_date = Column(DateTime(timezone=True), nullable=False)
    strength = Column(Numeric, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    position_sales = relationship("PositionSale", lazy=True, backref=backref(__tablename__, lazy=False))

    __table_args__ = (UniqueConstraint("implementation_run_id", "position_id", "signal_date"),)
