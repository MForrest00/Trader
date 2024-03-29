from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CryptocurrencyExchangeMarketCategory(Base):
    __tablename__ = "cryptocurrency_exchange_market_category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    description = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarket", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarketFeeType(Base):
    __tablename__ = "cryptocurrency_exchange_market_fee_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    description = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_markets = relationship(
        "CryptocurrencyExchangeMarket", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CryptocurrencyExchangeMarket(Base):
    __tablename__ = "cryptocurrency_exchange_market"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    cryptocurrency_exchange_id = Column(Integer, ForeignKey("cryptocurrency_exchange.id"), nullable=False)
    cryptocurrency_exchange_market_category_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_category.id"), nullable=False
    )
    base_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    quote_asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    cryptocurrency_exchange_market_fee_type_id = Column(
        Integer, ForeignKey("cryptocurrency_exchange_market_fee_type.id"), nullable=False
    )
    url = Column(String, nullable=False)
    coin_market_cap_id = Column(Integer, nullable=True)
    coin_market_cap_date_last_updated = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    cryptocurrency_exchange_market_stats = relationship(
        "CryptocurrencyExchangeMarketStat", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    # Many to one
    base_asset = relationship(
        "Asset", lazy=False, backref=backref(f"base_{__tablename__}s", lazy=True), foreign_keys=[base_asset_id]
    )
    quote_asset = relationship(
        "Asset", lazy=False, backref=backref(f"quote_{__tablename__}s", lazy=True), foreign_keys=[quote_asset_id]
    )

    __table_args__ = (
        UniqueConstraint(
            "cryptocurrency_exchange_id",
            "cryptocurrency_exchange_market_category_id",
            "base_asset_id",
            "quote_asset_id",
        ),
    )
