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
from trader.models.base import Base


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
