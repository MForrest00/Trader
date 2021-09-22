from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class AssetOHLCVGroup(Base):
    __tablename__ = "asset_ohlcv_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    base_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    quote_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    asset_ohlcv_implementations = relationship(
        "AssetOHLCVImplementation", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    asset_ohlcv_pulls = relationship("AssetOHLCVPull", lazy=True, backref=backref(__tablename__, lazy=False))

    # Many to one
    base_asset = relationship(
        "Asset", lazy=False, backref=backref(f"base_{__tablename__}s", lazy=True), foreign_keys=[base_asset_id]
    )
    quote_asset = relationship(
        "Asset", lazy=False, backref=backref(f"quote_{__tablename__}s", lazy=True), foreign_keys=[quote_asset_id]
    )

    __table_args__ = (UniqueConstraint("source_id", "base_asset_id", "quote_asset_id", "timeframe_id"),)


class AssetOHLCVPull(Base):
    __tablename__ = "asset_ohlcv_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_ohlcv_group_id = Column(Integer, ForeignKey("asset_ohlcv_group.id"), nullable=False)
    from_inclusive = Column(DateTime(timezone=True), nullable=False)
    to_exclusive = Column(DateTime(timezone=True), nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    asset_ohlcvs = relationship("AssetOHLCV", lazy=True, backref=backref(__tablename__, lazy=False))


class AssetOHLCV(Base):
    __tablename__ = "asset_ohlcv"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_ohlcv_pull_id = Column(Integer, ForeignKey("asset_ohlcv_pull.id"), nullable=False)
    date_open = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(33, 15), nullable=False)
    high = Column(Numeric(33, 15), nullable=False)
    low = Column(Numeric(33, 15), nullable=False)
    close = Column(Numeric(33, 15), nullable=False)
    volume = Column(Numeric(33, 15), nullable=False)
    date_high = Column(DateTime(timezone=True), nullable=True)
    date_low = Column(DateTime(timezone=True), nullable=True)

    # One to many
    asset_ohlcv_buy_signals = relationship("AssetOHLCVBuySignal", lazy=True, backref=backref(__tablename__, lazy=False))
