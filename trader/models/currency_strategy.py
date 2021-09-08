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


class CurrencyStrategyImplementationType(Base):
    __tablename__ = "currency_strategy_implementation_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_implementations = relationship(
        "CurrencyImplementation", lazy=True, backref=backref(__tablename__, lazy=False)
    )
    currency_strategies = relationship("CurrencyStrategy", lazy=True, backref=backref(__tablename__, lazy=False))


class CurrencyStrategy(Base):
    __tablename__ = "currency_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_implementation_type_id = Column(
        Integer, ForeignKey("currency_strategy_implementation_type.id"), nullable=False
    )
    name = Column(String(250), nullable=False)
    is_entrance = Column(Boolean, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_strategy_versions = relationship(
        "CurrencyStrategyVersion", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("currency_strategy_implementation_type_id", "name", "is_entrance"),)


class CurrencyStrategyVersion(Base):
    __tablename__ = "currency_strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_id = Column(Integer, ForeignKey("currency_strategy.id"), nullable=False)
    version = Column(String(250), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_implementation_versions = relationship(
        "CurrencyImplementationVersionXCurrencyStrategyVersion", lazy=True, back_populates=__tablename__
    )
    currency_strategy_version_parameters = relationship(
        "CurrencyStrategyVersionXCurrencyStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )

    __table_args__ = (UniqueConstraint("currency_strategy_id", "version"),)


class CurrencyStrategyVersionParameter(Base):
    __tablename__ = "currency_strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parameter = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_strategy_versions = relationship(
        "CurrencyStrategyVersionXCurrencyStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )


class CurrencyStrategyVersionXCurrencyStrategyVersionParameter(Base):
    __tablename__ = "currency_strategy_version_x_currency_strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_version_id = Column(Integer, ForeignKey("currency_strategy_version.id"), nullable=False)
    currency_strategy_version_parameter_id = Column(
        Integer, ForeignKey("currency_strategy_version_parameter.id"), nullable=False
    )
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    currency_strategy_version = relationship(
        "CurrencyStrategyVersion", lazy=False, back_populates="currency_strategy_version_parameters"
    )
    currency_strategy_version_parameter = relationship(
        "CurrencyStrategyVersionParameter", lazy=False, back_populates="currency_strategy_versions"
    )

    __table_args__ = (UniqueConstraint("currency_strategy_version_id", "currency_strategy_version_parameter_id"),)
