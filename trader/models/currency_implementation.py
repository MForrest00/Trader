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


class CurrencyImplementation(Base):
    __tablename__ = "currency_implementation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_implementation_type_id = Column(
        Integer, ForeignKey("currency_strategy_implementation_type.id"), nullable=False
    )
    name = Column(String(250), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_implementation_versions = relationship(
        "CurrencyImplementationVersion", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("currency_strategy_implementation_type_id", "name"),)


class CurrencyImplementationVersion(Base):
    __tablename__ = "currency_implementation_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_implementation_id = Column(Integer, ForeignKey("currency_implementation.id"), nullable=False)
    version = Column(String(250), nullable=False)
    source_code_md5_hash = Column(String(32), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_strategy_versions = relationship(
        "CurrencyImplementationVersionXCurrencyStrategyVersion", lazy=True, back_populates=__tablename__
    )

    __table_args__ = (UniqueConstraint("currency_implementation_id", "version"),)


class CurrencyImplementationVersionXCurrencyStrategyVersion(Base):
    __tablename__ = "currency_implementation_version_x_currency_strategy_version"
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_implementation_version_id = Column(
        Integer, ForeignKey("currency_implementation_version.id"), nullable=False
    )
    currency_strategy_version_id = Column(Integer, ForeignKey("currency_strategy_version.id"), nullable=False)
    currency_strategy_version_parameter_data = Column(JSONB, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_implementation_version = relationship(
        "CurrencyImplementationVersion", lazy=False, back_populates="currency_strategy_versions"
    )
    currency_strategy_version = relationship(
        "CurrencyStrategyVersion", lazy=False, back_populates="currency_implementation_versions"
    )
