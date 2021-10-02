from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class Implementation(Base):
    __tablename__ = "implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    quote_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    implementation_runs = relationship("ImplementationRun", lazy=True, backref=backref(__tablename__, lazy=False))

    __table_args__ = (UniqueConstraint("timeframe_id", "asset_id", "strategy_version_instance_id"),)


class ImplementationRun(Base):
    __tablename__ = "implementation_run"

    id = Column(Integer, primary_key=True, autoincrement=True)
    implementation_id = Column(Integer, ForeignKey("implementation.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to one
    asset_ohlcv_implementation_run = relationship(
        "AssetOHLCVImplementationRun", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    # One to many
    buy_signals = relationship("BuySignal", lazy=True, backref=backref(__tablename__, lazy=False))
    sell_signals = relationship("SellSignal", lazy=True, backref=backref(__tablename__, lazy=False))


class AssetOHLCVImplementationRun(Base):
    __tablename__ = "asset_ohlcv_implementation_run"

    id = Column(Integer, primary_key=True, autoincrement=True)
    implementation_run_id = Column(Integer, ForeignKey("implementation_run.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    quote_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
