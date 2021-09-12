from sqlalchemy import (
    Boolean,
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


class CryptocurrencyExchangeType(Base):
    __tablename__ = "cryptocurrency_exchange_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    description = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchanges = relationship(
        "CryptocurrencyExchange", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchange(Base):
    __tablename__ = "cryptocurrency_exchange"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False, unique=True)
    cryptocurrency_exchange_type_id = Column(Integer, ForeignKey("cryptocurrency_exchange_type.id"), nullable=True)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String, nullable=True)
    source_date_launched = Column(DateTime(timezone=True), nullable=True)
    source_date_last_updated = Column(DateTime(timezone=True), nullable=True)

    # One to one
    enabled_cryptocurrency_exchange = relationship(
        "EnabledCryptocurrencyExchange", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    # One to many
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarket", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    cryptocurrency_exchange_market_stat_pulls = relationship(
        "CryptocurrencyExchangeMarketStatPull", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    cryptocurrency_exchange_ranks = relationship(
        "CryptocurrencyExchangeRank", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    # Many to many
    countries = relationship("CountryXCryptocurrencyExchange", lazy=True, back_populates=__tablename__)
    standard_currencies = relationship(
        "CryptocurrencyExchangeXStandardCurrency", lazy=True, back_populates=__tablename__
    )


class CryptocurrencyExchangeXStandardCurrency(Base):
    __tablename__ = "cryptocurrency_exchange_x_standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    standard_currency_id = Column(Integer, ForeignKey("standard_currency.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    cryptocurrency_exchange = relationship("CryptocurrencyExchange", lazy=False, back_populates="standard_currencies")
    standard_currency = relationship("StandardCurrency", lazy=False, back_populates="cryptocurrency_exchanges")

    __table_args__ = (UniqueConstraint("cryptocurrency_exchange_id", "standard_currency_id"),)
