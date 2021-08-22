from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CryptocurrencyRankSnapshot(Base):
    __tablename__ = "cryptocurrency_rank_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    is_historical = Column(Boolean, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    cryptocurrency_ranks = relationship("CryptocurrencyRank", lazy=True, backref=backref(__tablename__, lazy=False))


class CryptocurrencyRank(Base):
    __tablename__ = "cryptocurrency_rank"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cryptocurrency_rank_snapshot_id = Column(Integer, ForeignKey("cryptocurrency_rank_snapshot.id"), nullable=False)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrency.id"), nullable=False)
    rank = Column(SmallInteger, nullable=False)
    usd_market_cap = Column(Numeric(33, 15), nullable=True)
    usd_price = Column(Numeric(33, 15), nullable=False)
    usd_volume_24h = Column(Numeric(33, 15), nullable=False)
    circulating_supply = Column(Numeric(33, 15), nullable=True)
    total_supply = Column(Numeric(33, 15), nullable=True)
