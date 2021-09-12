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


class Strategy(Base):
    __tablename__ = "strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    is_entry = Column(Boolean, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    strategy_versions = relationship("StrategyVersion", lazy=True, backref=backref(__tablename__, lazy=False))

    __table_args__ = (UniqueConstraint("name", "is_entry"),)


class StrategyVersion(Base):
    __tablename__ = "strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategy.id"), nullable=False)
    version = Column(String, nullable=False)
    source_code_md5_hash = Column(String(32), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    strategy_version_parameters = relationship(
        "StrategyVersionXStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )

    __table_args__ = (UniqueConstraint("strategy_id", "version"),)


class StrategyVersionParameter(Base):
    __tablename__ = "strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parameter = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    strategy_versions = relationship(
        "StrategyVersionXStrategyVersionParameter", lazy=True, back_populates=__tablename__
    )


class StrategyVersionXStrategyVersionParameter(Base):
    __tablename__ = "strategy_version_x_strategy_version_parameter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_version_id = Column(Integer, ForeignKey("strategy_version.id"), nullable=False)
    strategy_version_parameter_id = Column(Integer, ForeignKey("strategy_version_parameter.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    strategy_version = relationship("StrategyVersion", lazy=False, back_populates="strategy_version_parameters")
    strategy_version_parameter = relationship(
        "StrategyVersionParameter", lazy=False, back_populates="strategy_versions"
    )

    __table_args__ = (UniqueConstraint("strategy_version_id", "strategy_version_parameter_id"),)
