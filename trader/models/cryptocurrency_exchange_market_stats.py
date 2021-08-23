from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CryptocurrencyExchangeMarketStatsPull(Base):
    __tablename__ = "cryptocurrency_exchange_market_stats_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("crypotocurrency_exchange.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    cryptocurrency_exchange_market_stats = relationship(
        "CryptocurrencyExchangeMarketStats", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarketStats(Base):
    __tablename__ = "cryptocurrency_exchange_market_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_exchange_market_stats_pull_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_stats_pull.id"), nullable=False
    )
    cryptocurrency_exchange_market_id = Column(Integer, ForeignKey("cryptocurrency_exchange_market.id"), nullable=False)
