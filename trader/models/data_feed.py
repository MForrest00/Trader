from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class DataFeed(Base):
    __tablename__ = "data_feed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    strategy_versions = relationship("DataFeedXStrategyVersion", lazy=True, back_populates=__tablename__)


class DataFeedXStrategyVersion(Base):
    __tablename__ = "data_feed_x_strategy_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_feed_id = Column(Integer, ForeignKey("data_feed.id"), nullable=False)
    strategy_version_id = Column(Integer, ForeignKey("strategy_version.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    data_feed = relationship("DataFeed", lazy=False, back_populates="strategy_versions")
    strategy_version = relationship("StrategyVersion", lazy=False, back_populates="data_feeds")

    __table_args__ = (UniqueConstraint("data_feed_id", "strategy_version_id"),)
