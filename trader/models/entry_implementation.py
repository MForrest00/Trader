from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class EntryImplementation(Base):
    __tablename__ = "entry_implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    base_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    entry_implementation_runs = relationship(
        "EntryImplementationRun", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("timeframe_id", "asset_id", "strategy_version_instance_id"),)


class EntryImplementationRun(Base):
    __tablename__ = "entry_implementation_run"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_implementation_id = Column(Integer, ForeignKey("entry_implementation.id"), nullable=False)
    extra_fields = Column(JSONB, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    buy_signals = relationship("BuySignal", lazy=True, backref=backref(__tablename__, lazy=False))
