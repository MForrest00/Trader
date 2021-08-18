from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.persistence.models.base import Base


class CryptocurrencyExchangeRankPull(Base):
    __tablename__ = "cryptocurrency_exchange_rank_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    cryptocurrency_exchange_ranks = relationship(
        "CryptocurrencyExchangeRank", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeRank(Base):
    __tablename__ = "cryptocurrency_exchange_rank"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_exchange_rank_pull_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_rank_pull.id"), nullable=False
    )
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    rank = Column(SmallInteger, nullable=False)
    spot_vol_24h = Column(Numeric(33, 15), nullable=False)
    derivatives_vol_24h = Column(Numeric(33, 15), nullable=False)
    derivatives_open_interests = Column(Numeric(33, 15), nullable=False)
    weekly_visits = Column(Integer, nullable=False)
    liquidity_score = Column(Numeric(8, 4), nullable=False)
    market_share_percentage = Column(Numeric(7, 4), nullable=False)
    maker_fee = Column(Numeric(8, 4), nullable=False)
    taker_fee = Column(Numeric(8, 4), nullable=False)
