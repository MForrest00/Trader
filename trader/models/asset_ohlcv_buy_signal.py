from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func
from trader.models.base import Base


class AssetOHLCVBuySignal(Base):
    __tablename__ = "asset_ohlcv_buy_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_ohlcv_implementation_run_id = Column(Integer, ForeignKey("asset_ohlcv_implementation_run.id"), nullable=False)
    asset_ohlcv_id = Column(Integer, ForeignKey("asset_ohlcv.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("asset_ohlcv_implementation_run_id", "asset_ohlcv_id"),)
