from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class DataFeed(Base):
    __tablename__ = "data_feed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    base_strategy_versions = relationship(
        "StrategyVersion", lazy=True, backref=backref(f"base_{__tablename__}", lazy=False)
    )

    # Many to many
    supplemental_strategy_versions = relationship(
        "StrategyVersionXSupplementalDataFeed", lazy=True, back_populates=__tablename__
    )
