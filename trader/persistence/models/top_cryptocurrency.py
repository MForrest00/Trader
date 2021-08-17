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
from trader.persistence.models.base import Base


class TopCryptocurrencySnapshot(Base):
    __tablename__ = "top_cryptocurrency_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    is_historical = Column(Boolean, nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    top_cryptocurrencies = relationship("TopCryptocurrency", lazy=True, backref=backref(__tablename__, lazy=False))


class TopCryptocurrency(Base):
    __tablename__ = "top_cryptocurrency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    top_cryptocurrency_snapshot_id = Column(Integer, ForeignKey("top_cryptocurrency_snapshot.id"), nullable=False)
    rank = Column(SmallInteger, nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    usd_market_cap = Column(Numeric(33, 15), nullable=True)
    usd_price = Column(Numeric(33, 15), nullable=False)
    circulating_supply = Column(Numeric(33, 15), nullable=True)
    total_supply = Column(Numeric(33, 15), nullable=True)
