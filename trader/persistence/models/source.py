from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.persistence.models.base import Base


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
