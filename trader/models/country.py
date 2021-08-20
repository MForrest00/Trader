from sqlalchemy import (
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
    name = Column(String(250), nullable=False)
    official_name = Column(String(250), nullable=False)
    iso_alpha_2_code = Column(String(2), nullable=False, unique=True)
    iso_alpha_3_code = Column(String(3), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("CountryCurrency", lazy=True, back_populates=__tablename__)
    cryptocurrency_exchanges = relationship("CryptocurrencyExchangeCountry", lazy=True, back_populates=__tablename__)


class CountryCurrency(Base):
    __tablename__ = "country_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    country = relationship("Country", lazy=False, back_populates="currencies")
    currency = relationship("Currency", lazy=False, back_populates="countries")

    __table_args__ = (UniqueConstraint("country_id", "currency_id"),)
