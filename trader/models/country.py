from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String, nullable=False)
    official_name = Column(String, nullable=False)
    iso_alpha_2_code = Column(String(2), nullable=False, unique=True)
    iso_alpha_3_code = Column(String(3), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    cryptocurrency_exchanges = relationship("CountryXCryptocurrencyExchange", lazy=True, back_populates=__tablename__)
    standard_currencies = relationship("CountryXStandardCurrency", lazy=True, back_populates=__tablename__)


class CountryXCryptocurrencyExchange(Base):
    __tablename__ = "country_x_cryptocurrency_exchange"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    country = relationship("Country", lazy=False, back_populates="cryptocurrency_exchanges")
    cryptocurrency_exchange = relationship("CryptocurrencyExchange", lazy=False, back_populates="countries")

    __table_args__ = (UniqueConstraint("country_id", "cryptocurrency_exchange_id"),)


class CountryXStandardCurrency(Base):
    __tablename__ = "country_x_standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    standard_currency_id = Column(Integer, ForeignKey("standard_currency.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    country = relationship("Country", lazy=False, back_populates="standard_currencies")
    standard_currency = relationship("StandardCurrency", lazy=False, back_populates="countries")

    __table_args__ = (UniqueConstraint("country_id", "standard_currency_id"),)
