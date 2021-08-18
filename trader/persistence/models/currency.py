from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.persistence.models.base import Base


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    cryptocurrency = relationship(
        "Cryptocurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    currency_tags = relationship("CurrencyCurrencyTag", lazy=True, back_populates="currency")
    currency_ohlcv_pulls = relationship("CurrencyOHLCVPull", lazy=True, backref=backref(__tablename__, lazy=False))

    __table_args__ = (UniqueConstraint("name", "symbol", name=f"uc_{__tablename__}_name_symbol"),)


class CurrencyTag(Base):
    __tablename__ = "currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    tag = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("CurrencyCurrencyTag", lazy=True, back_populates="currency_tag")


class CurrencyCurrencyTag(Base):
    __tablename__ = "currency_currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    currency_tag_id = Column(Integer, ForeignKey("currency_tag.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency = relationship("Currency", lazy=True, back_populates="currency_tags")
    currency_tag = relationship("CurrencyTag", lazy=True, back_populates="currencies")

    __table_args__ = (
        UniqueConstraint("currency_id", "currency_tag_id", name=f"uc_{__tablename__}_currency_id_currency_tag_id"),
    )


class CryptocurrencyPlatform(Base):
    __tablename__ = "cryptocurrency_platform"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String(50), nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    cryptocurrencies = relationship("Cryptocurrency", lazy=True, backref=backref("cryptocurrency_platform", lazy=True))

    __table_args__ = (UniqueConstraint("name", "symbol", name=f"uc_{__tablename__}_name_symbol"),)


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False, unique=True)
    max_supply = Column(Numeric(33, 15), nullable=True)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String(50), nullable=True)
    source_date_added = Column(DateTime, nullable=True)
    source_date_last_updated = Column(DateTime, nullable=True)
    cryptocurrency_platform_id = Column(Integer, ForeignKey("cryptocurrency_platform.id"), nullable=True)

    cryptocurrency_ranks = relationship("CryptocurrencyRank", lazy=True, backref=backref(__tablename__, lazy=False))
