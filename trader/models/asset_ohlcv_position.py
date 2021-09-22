from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from trader.models.base import Base


class AssetOHLCVPosition(Base):
    __tablename__ = "asset_ohlcv_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    asset_ohlcv_buy_signal_id = Column(Integer, ForeignKey("asset_ohlcv_buy_signal.id"), nullable=False)
    bought_size = Column(Numeric(33, 15), nullable=False)
    data = Column(JSONB, nullable=True)
    close_asset_ohlcv_implementation_run_id = Column(
        Integer, ForeignKey("asset_ohlcv_implementation_run.id"), nullable=True
    )
    close_asset_ohlcv_id = Column(Integer, ForeignKey("asset_ohlcv.id"), nullable=True)
    date_opened = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_closed = Column(DateTime(timezone=True), nullable=True)
