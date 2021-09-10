from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class CurrencyOHLCVImplementation(Base):
    __tablename__ = "currency_ohlcv_implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcv_implementation_versions = relationship(
        "CurrencyOHLCVImplementationVersion", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class CurrencyOHLCVImplementationVersion(Base):
    __tablename__ = "currency_ohlcv_implementation_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_implementation_id = Column(Integer, ForeignKey("currency_implementation.id"), nullable=False)
    version = Column(String(250), nullable=False)
    source_code_md5_hash = Column(String(32), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_ohlcv_strategy_versions = relationship(
        "CurrencyOHLCVImplementationVersionXCurrencyOHLCVStrategyVersion", lazy=True, back_populates=__tablename__
    )

    __table_args__ = (UniqueConstraint("currency_ohlcv_implementation_id", "version"),)


class CurrencyOHLCVImplementationVersionXCurrencyOHLCVStrategyVersion(Base):
    __tablename__ = "currency_ohlcv_implementation_version_x_currency_ohlcv_strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_implementation_version_id = Column(
        Integer, ForeignKey("currency_ohlcv_implementation_version.id"), nullable=False
    )
    currency_ohlcv_strategy_version_id = Column(
        Integer, ForeignKey("currency_ohlcv_strategy_version.id"), nullable=False
    )
    currency_ohlcv_strategy_version_parameter_data = Column(JSONB, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_ohlcv_implementation_version = relationship(
        "CurrencyOHLCVImplementationVersion", lazy=False, back_populates="currency_ohlcv_strategy_versions"
    )
    currency_ohlcv_strategy_version = relationship(
        "CurrencyOHLCVStrategyVersion", lazy=False, back_populates="currency_ohlcv_implementation_versions"
    )
