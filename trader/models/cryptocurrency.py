from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CryptocurrencyPlatform(Base):
    __tablename__ = "cryptocurrency_platform"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrencies = relationship("Cryptocurrency", lazy=True, backref=backref("cryptocurrency_platform", lazy=True))

    __table_args__ = (UniqueConstraint("name", "symbol"),)


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, unique=True)
    max_supply = Column(Numeric, nullable=True)
    source_entity_id = Column(Integer, nullable=True)
    source_slug = Column(String, nullable=True)
    source_date_added = Column(DateTime(timezone=True), nullable=True)
    source_date_last_updated = Column(DateTime(timezone=True), nullable=True)
    cryptocurrency_platform_id = Column(Integer, ForeignKey("cryptocurrency_platform.id"), nullable=True)

    # One to many
    cryptocurrency_ranks = relationship("CryptocurrencyRank", lazy=True, backref=backref(__tablename__, lazy=False))
