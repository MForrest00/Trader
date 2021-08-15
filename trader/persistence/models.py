from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.connections.database import database


Base = declarative_base()


class SourceType(Base):
    __tablename__ = "source_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    sources = relationship("Source", lazy=True, backref=backref(__tablename__, lazy=False))


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    source_type_id = Column(Integer, ForeignKey("source_type.id"), nullable=False)
    url = Column(String(250), nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency_platforms = relationship("CurrencyPlatform", lazy=True, backref=backref(__tablename__, lazy=True))
    currencies = relationship("Currency", lazy=True, backref=backref(__tablename__, lazy=True))
    currency_tags = relationship("CurrencyTag", lazy=True, backref=backref(__tablename__, lazy=True))
    currency_currency_tags = relationship("CurrencyCurrencyTag", lazy=True, backref=backref(__tablename__, lazy=True))
    top_cryptocurrency_snapshots = relationship(
        "TopCryptocurrencySnapshot", lazy=True, backref=backref(__tablename__, lazy=True)
    )
    currency_ohlcv_pulls = relationship("CurrencyOHLCVPull", lazy=True, backref=backref(__tablename__, lazy=True))


class CurrencyPlatform(Base):
    __tablename__ = "currency_platform"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("Currency", lazy=True, backref=backref("currency_platform", lazy=True))

    __table_args__ = (UniqueConstraint("name", "symbol", name=f"uc_{__tablename__}_name_symbol"),)


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    is_cryptocurrency = Column(Boolean, nullable=False, default=True)
    max_supply = Column(Numeric(33, 15), nullable=True)
    source_date_added = Column(DateTime, nullable=True)
    currency_platform_id = Column(Integer, ForeignKey("currency_platform.id"), nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency_tags = relationship("CurrencyCurrencyTag", lazy=True, back_populates="currency")

    __table_args__ = (
        UniqueConstraint(
            "name", "symbol", "is_cryptocurrency", name=f"uc_{__tablename__}_name_symbol_is_cryptocurrency"
        ),
    )


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
    usd_market_cap = Column(Numeric(33, 15), nullable=False)
    usd_price = Column(Numeric(33, 15), nullable=False)
    circulating_supply = Column(Numeric(33, 15), nullable=False)
    total_supply = Column(Numeric(33, 15), nullable=False)


class Timeframe(Base):
    __tablename__ = "timeframe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ccxt_label = Column(String(3), nullable=False)
    seconds_length = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())


class CurrencyOHLCVPull(Base):
    __tablename__ = "currency_ohlcv_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    base_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    from_inclusive = Column(DateTime, nullable=False)
    to_exclusive = Column(DateTime, nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency_ohlcvs = relationship("CurrencyOHLCV", lazy=True, backref=backref(__tablename__, lazy=False))


class CurrencyOHLCV(Base):
    __tablename__ = "currency_ohlcv"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_pull_id = Column(Integer, ForeignKey("currency_ohlcv_pull.id"), nullable=False)
    open = Column(Numeric(33, 15), nullable=False)
    high = Column(Numeric(33, 15), nullable=False)
    low = Column(Numeric(33, 15), nullable=False)
    close = Column(Numeric(33, 15), nullable=False)
    volume = Column(Numeric(33, 15), nullable=False)


def initialize_models() -> None:
    Base.metadata.create_all(database)
