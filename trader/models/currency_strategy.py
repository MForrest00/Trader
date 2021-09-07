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


class CurrencyStrategyType(Base):
    __tablename__ = "currency_strategy_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_strategies = relationship("CurrencyStrategy", lazy=True, backref=backref(__tablename__, lazy=False))


class CurrencyStrategy(Base):
    __tablename__ = "currency_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_type_id = Column(Integer, ForeignKey("currency_strategy_type.id"), nullable=False)
    name = Column(String(250), nullable=False)
    is_entrance = Column(Boolean, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    currency_strategy_versions = relationship(
        "CurrencyStrategyVersion", lazy=True, backref=backref(__tablename__, lazy=False)
    )

    __table_args__ = (UniqueConstraint("currency_strategy_type_id", "name", "is_entrance"),)


class CurrencyStrategyVersion(Base):
    __tablename__ = "currency_strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_strategy_id = Column(Integer, ForeignKey("currency_strategy.id"), nullable=False)
    version = Column(String(250), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("currency_strategy_id", "version"),)
