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


class CurrencyType(Base):
    __tablename__ = "currency_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("Currency", lazy=True, backref=backref(__tablename__, lazy=True))


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    currency_type_id = Column(Integer, ForeignKey("currency_type.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    cryptocurrency = relationship(
        "Cryptocurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )
    standard_currency = relationship(
        "StandardCurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    currency_tags = relationship("CurrencyCurrencyTag", lazy=True, back_populates=__tablename__)
    countries = relationship("CountryCurrency", lazy=True, back_populates=__tablename__)

    __table_args__ = (UniqueConstraint("name", "symbol", "currency_type_id"),)


class CurrencyTag(Base):
    __tablename__ = "currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    tag = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("CurrencyCurrencyTag", lazy=True, back_populates=__tablename__)


class CurrencyCurrencyTag(Base):
    __tablename__ = "currency_currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    currency_tag_id = Column(Integer, ForeignKey("currency_tag.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency = relationship("Currency", lazy=False, back_populates="currency_tags")
    currency_tag = relationship("CurrencyTag", lazy=False, back_populates="currencies")

    __table_args__ = (UniqueConstraint("currency_id", "currency_tag_id"),)
