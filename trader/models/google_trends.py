from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class GoogleTrendsPullGeo(Base):
    __tablename__ = "google_trends_pull_geo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(25), nullable=False, unique=True)
    name = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    google_trends_pulls = relationship("GoogleTrendsPull", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrendsPull(Base):
    __tablename__ = "google_trends_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    google_trends_pull_geo_id = Column(Integer, ForeignKey("google_trends_pull_geo.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    from_inclusive = Column(DateTime, nullable=False)
    to_exclusive = Column(DateTime, nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    google_trends_data = relationship("GoogleTrends", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrendsPullKeyword(Base):
    __tablename__ = "google_trends_pull_keyword"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    google_trends_data = relationship("GoogleTrends", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrends(Base):
    __tablename__ = "google_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_trends_pull_id = Column(Integer, ForeignKey("google_trends_pull.id"), nullable=False)
    google_trends_pull_keyword_id = Column(Integer, ForeignKey("google_trends_pull_keyword.id"), nullable=False)
    data_date = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    is_partial = Column(Boolean, nullable=False, default=False)
