from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CryptocurrencyExchangeMarketStatPull(Base):
    __tablename__ = "cryptocurrency_exchange_market_stat_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    cryptocurrency_exchange_market_stats = relationship(
        "CryptocurrencyExchangeMarketStat", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarketStat(Base):
    __tablename__ = "cryptocurrency_exchange_market_stat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_exchange_market_stat_pull_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_stat_pull.id"), nullable=False
    )
    cryptocurrency_exchange_market_id = Column(Integer, ForeignKey("cryptocurrency_exchange_market.id"), nullable=False)
    price = Column(Numeric, nullable=False)
    usd_volume_24h = Column(Numeric, nullable=False)
    base_asset_volume_24h = Column(Numeric, nullable=False)
    quote_asset_volume_24h = Column(Numeric, nullable=False)
    usd_depth_negative_two = Column(Numeric, nullable=True)
    usd_depth_positive_two = Column(Numeric, nullable=True)
    source_score = Column(Numeric, nullable=True)
    source_liquidity_score = Column(Numeric, nullable=True)
    source_reputation = Column(Numeric, nullable=True)
    source_outlier_detected = Column(Boolean, nullable=False)
    source_price_excluded = Column(Boolean, nullable=False)
    source_volume_excluded = Column(Boolean, nullable=False)
