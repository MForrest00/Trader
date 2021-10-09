from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledStrategyVersionInstance(Base):
    __tablename__ = "enabled_strategy_version_instance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    history = relationship(
        "EnabledStrategyVersionInstanceHistory",
        lazy=False,
        order_by="desc(EnabledStrategyVersionInstanceHistory.date_created)",
        backref=backref(__tablename__, lazy=False),
    )

    __table_args__ = (UniqueConstraint("strategy_version_instance_id", "timeframe_id"),)


class EnabledStrategyVersionInstanceHistory(Base):
    __tablename__ = "enabled_strategy_version_instance_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enabled_strategy_version_instance_id = Column(
        Integer, ForeignKey("enabled_strategy_version_instance.id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    priority = Column(SmallInteger, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
