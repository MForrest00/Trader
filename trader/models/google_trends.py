from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class GoogleTrendsGeo(Base):
    __tablename__ = "google_trends_geo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_groups = relationship("GoogleTrendsGroup", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrendsGprop(Base):
    __tablename__ = "google_trends_gprop"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_groups = relationship("GoogleTrendsGroup", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrendsKeywords(Base):
    __tablename__ = "google_trends_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keywords = Column(ARRAY(String), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_groups = relationship("GoogleTrendsGroup", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrendsGroup(Base):
    __tablename__ = "google_trends_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    google_trends_geo_id = Column(Integer, ForeignKey("google_trends_geo.id"), nullable=False)
    google_trends_gprop_id = Column(Integer, ForeignKey("google_trends_gprop.id"), nullable=False)
    google_trends_keywords_id = Column(Integer, ForeignKey("google_trends_keywords.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_pulls = relationship("GoogleTrendsPull", lazy=True, backref=backref(__tablename__, lazy=False))

    __table_args__ = (
        UniqueConstraint(
            "source_id", "google_trends_geo_id", "google_trends_gprop_id", "google_trends_keywords_id", "timeframe_id"
        ),
    )


class GoogleTrendsPull(Base):
    __tablename__ = "google_trends_pull"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_trends_group_id = Column(Integer, ForeignKey("google_trends_group.id"), nullable=False)
    from_inclusive = Column(DateTime(timezone=True), nullable=True)
    to_exclusive = Column(DateTime(timezone=True), nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_pull_steps = relationship(
        "GoogleTrendsPullStep", lazy=True, backref=backref(__tablename__, lazy=False)
    )


class GoogleTrendsPullStep(Base):
    __tablename__ = "google_trends_pull_step"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_trends_pull_id = Column(Integer, ForeignKey("google_trends_pull.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    from_date = Column(DateTime(timezone=True), nullable=False)
    to_date = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    google_trends_data = relationship("GoogleTrends", lazy=True, backref=backref(__tablename__, lazy=False))


class GoogleTrends(Base):
    __tablename__ = "google_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_trends_pull_step_id = Column(Integer, ForeignKey("google_trends_pull_step.id"), nullable=False)
    google_trends_keyword_index = Column(SmallInteger, nullable=False)
    data_date = Column(DateTime(timezone=True), nullable=False)
    value = Column(Integer, nullable=False)
    is_partial = Column(Boolean, nullable=False, default=False)
