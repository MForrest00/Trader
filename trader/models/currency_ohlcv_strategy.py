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


class CurrencyOHLCVStrategy(Base):
    __tablename__ = "currency_ohlcv_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, unique=True)
    is_entrance = Column(Boolean, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_ohlcv_strategy_versions = relationship(
        "CurrencyOHLCVStrategyVersion", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("name", "is_entrance"),)


class CurrencyOHLCVStrategyVersion(Base):
    __tablename__ = "currency_ohlcv_strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_strategy_id = Column(Integer, ForeignKey("currency_ohlcv_strategy.id"), nullable=False)
    version = Column(String(250), nullable=False)
    source_code_md5_hash = Column(String(32), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_ohlcv_implementation_versions = relationship(
        "CurrencyOHLCVImplementationVersionXCurrencyOHLCVStrategyVersion", lazy=True, back_populates=__tablename__
    )
    currency_ohlcv_strategy_version_parameters = relationship(
        "CurrencyOHLCVStrategyVersionXCurrencyOHLCVStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )

    __table_args__ = (UniqueConstraint("currency_ohlcv_strategy_id", "version"),)


class CurrencyOHLCVStrategyVersionParameter(Base):
    __tablename__ = "currency_ohlcv_strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parameter = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_ohlcv_strategy_versions = relationship(
        "CurrencyOHLCVStrategyVersionXCurrencyOHLCVStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )


class CurrencyOHLCVStrategyVersionXCurrencyOHLCVStrategyVersionParameter(Base):
    __tablename__ = "currency_ohlcv_strategy_version_x_currency_ohlcv_strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_ohlcv_strategy_version_id = Column(
        Integer, ForeignKey("currency_ohlcv_strategy_version.id"), nullable=False
    )
    currency_ohlcv_strategy_version_parameter_id = Column(
        Integer, ForeignKey("currency_ohlcv_strategy_version_parameter.id"), nullable=False
    )
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_ohlcv_strategy_version = relationship(
        "CurrencyOHLCVStrategyVersion", lazy=False, back_populates="currency_ohlcv_strategy_version_parameters"
    )
    currency_ohlcv_strategy_version_parameter = relationship(
        "CurrencyOHLCVStrategyVersionParameter", lazy=False, back_populates="currency_ohlcv_strategy_versions"
    )

    __table_args__ = (
        UniqueConstraint("currency_ohlcv_strategy_version_id", "currency_ohlcv_strategy_version_parameter_id"),
    )
