from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class ExitImplementation(Base):
    __tablename__ = "exit_implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    exit_implementation_runs = relationship(
        "ExitImplementationRun", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("timeframe_id", "position_id", "strategy_version_instance_id"),)


class ExitImplementationRun(Base):
    __tablename__ = "exit_implementation_run"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exit_implementation_id = Column(Integer, ForeignKey("exit_implementation.id"), nullable=False)
    extra_fields = Column(JSONB, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    sell_signals = relationship("SellSignal", lazy=True, backref=backref(__tablename__, lazy=False))
