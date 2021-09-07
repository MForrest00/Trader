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


class CurrencyType(Base):
    __tablename__ = "currency_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currencies = relationship("Currency", lazy=True, backref=backref(__tablename__, lazy=False))


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    currency_type_id = Column(Integer, ForeignKey("currency_type.id"), nullable=False)
    name = Column(String(250), nullable=True)
    symbol = Column(String(25), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to one
    cryptocurrency = relationship(
        "Cryptocurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )
    enabled_quote_currency = relationship(
        "EnabledQuoteCurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )
    standard_currency = relationship(
        "StandardCurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    # Many to many
    currency_tags = relationship("CurrencyXCurrencyTag", lazy=True, back_populates=__tablename__)

    __table_args__ = (UniqueConstraint("symbol", "currency_type_id"),)


class CurrencyTag(Base):
    __tablename__ = "currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    tag = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currencies = relationship("CurrencyXCurrencyTag", lazy=True, back_populates=__tablename__)


class CurrencyXCurrencyTag(Base):
    __tablename__ = "currency_x_currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    currency_tag_id = Column(Integer, ForeignKey("currency_tag.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency = relationship("Currency", lazy=False, back_populates="currency_tags")
    currency_tag = relationship("CurrencyTag", lazy=False, back_populates="currencies")

    __table_args__ = (UniqueConstraint("currency_id", "currency_tag_id"),)
