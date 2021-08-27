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


class CryptocurrencyExchangeMarketCategory(Base):
    __tablename__ = "cryptocurrency_exchange_market_category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarkets", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarketFeeType(Base):
    __tablename__ = "cryptocurrency_exchange_market_fee_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarkets", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarket(Base):
    __tablename__ = "cryptocurrency_exchange_market"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("crypotocurrency_exchange.id"), nullable=False)
    cryptocurrency_exchange_market_category_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_category.id"), nullable=False
    )
    base_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    cryptocurrency_exchange_market_fee_type_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_fee_type.id"), nullable=False
    )
    market_url = Column(String(250), nullable=False)
    source_entity_id = Column(Integer, nullable=True)
    source_date_last_updated = Column(DateTime(timezone=True), nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_market_stats = relationship(
        "CryptocurrencyExchangeMarketStats", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    # Many to one
    base_currency = relationship(
        "Currency", lazy=False, backref=backref(f"base_{__tablename__}s", lazy=True), foreign_keys=[base_currency_id]
    )
    quote_currency = relationship(
        "Currency", lazy=False, backref=backref(f"quote_{__tablename__}s", lazy=True), foreign_keys=[quote_currency_id]
    )

    __table_args__ = (UniqueConstraint("cryptocurrency_exchange_id", "base_currency_id", "quote_currency_id"),)
