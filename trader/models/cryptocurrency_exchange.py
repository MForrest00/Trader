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


class CryptocurrencyExchange(Base):
    __tablename__ = "cryptocurrency_exchange"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False, unique=True)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String(50), nullable=True)
    source_date_launched = Column(DateTime(timezone=True), nullable=True)
    source_date_last_updated = Column(DateTime(timezone=True), nullable=True)

    cryptocurrency_exchange_ranks = relationship(
        "CryptocurrencyExchangeRank", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    countries = relationship("CountryCryptocurrencyExchange", lazy=True, back_populates=__tablename__)
    standard_currencies = relationship(
        "CryptocurrencyExchangeStandardCurrency", lazy=True, back_populates=__tablename__
    )


class CryptocurrencyExchangeStandardCurrency(Base):
    __tablename__ = "cryptocurrency_exchange_standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    standard_currency_id = Column(Integer, ForeignKey("standard_currency.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    cryptocurrency_exchange = relationship("CryptocurrencyExchange", lazy=False, back_populates="standard_currencies")
    standard_currency = relationship("StandardCurrency", lazy=False, back_populates="cryptocurrency_exchanges")

    __table_args__ = (UniqueConstraint("cryptocurrency_exchange_id", "standard_currency_id"),)
