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


class SourceType(Base):
    __tablename__ = "source_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    sources = relationship("Source", lazy=True, backref=backref(__tablename__, lazy=False))


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=True)
    name = Column(String(250), nullable=False)
    source_type_id = Column(Integer, ForeignKey("source_type.id"), nullable=False)
    url = Column(String(250), nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Internal one to many
    populated_sources = relationship("Source", lazy=True, backref=backref(__tablename__, lazy=True), remote_side=[id])

    # One to one
    cryptocurrency_exchange = relationship(
        "CryptocurrencyExchange", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    # One to many
    countries = relationship("Country", lazy=True, backref=backref(__tablename__, lazy=True))
    country_cryptocurrency_exchanges = relationship(
        "CountryCryptocurrencyExchange", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    country_currencies = relationship("CountryCurrency", lazy=True, backref=backref(__tablename__, lazy=True))
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarket", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    cryptocurrency_exchange_market_stats_pulls = relationship(
        "CryptocurrencyExchangeMarketStatsPull", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    cryptocurrency_exchange_rank_pulls = relationship(
        "CryptocurrencyExchangeRankPull", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    cryptocurrency_platforms = relationship(
        "CryptocurrencyPlatform", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    cryptocurrency_rank_snapshots = relationship(
        "CryptocurrencyRankSnapshot", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    currencies = relationship("Currency", lazy=True, backref=backref(__tablename__, lazy=True))
    currency_currency_tags = relationship("CurrencyCurrencyTag", lazy=True, backref=backref(__tablename__, lazy=True))
    currency_ohlcv_pulls = relationship("CurrencyOHLCVPull", lazy=True, backref=backref(__tablename__, lazy=True))
    currency_tags = relationship("CurrencyTag", lazy=True, backref=backref(__tablename__, lazy=True))
    google_trends_pulls = relationship("GoogleTrendsPull", lazy=True, backref=backref(__tablename__, lazy=True))

    __table_args__ = (UniqueConstraint("name", "source_type_id"),)
