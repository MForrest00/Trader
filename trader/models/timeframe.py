from sqlalchemy import Column, DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class Timeframe(Base):
    __tablename__ = "timeframe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_label = Column(String, nullable=True, unique=True)
    seconds_length = Column(Integer, nullable=True)
    unit = Column(String(1), nullable=False)
    amount = Column(SmallInteger, nullable=False)
    ccxt_label = Column(String, nullable=True, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    asset_ohlcv_groups = relationship("AssetOHLCVGroup", lazy=True, backref=backref(__tablename__, lazy=False))
    enabled_strategy_version_instances = relationship(
        "EnabledStrategyVersionInstance", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    google_trends_groups = relationship("GoogleTrendsGroup", lazy=True, backref=backref(__tablename__, lazy=False))
    google_trends_pull_steps = relationship(
        "GoogleTrendsPullStep", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    implementations = relationship("Implementation", lazy=True, backref=backref(__tablename__, lazy=False))
