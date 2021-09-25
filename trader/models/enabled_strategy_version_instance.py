from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledStrategyVersionInstance(Base):
    __tablename__ = "enabled_strategy_version_instance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_version_instance_id = Column(Integer, ForeignKey("strategy_version_instance.id"), nullable=False)
    timeframe_id = Column(Integer, ForeignKey("timeframe.id"), nullable=False)
    priority = Column(SmallInteger, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)
    date_enabled = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("strategy_version_instance_id", "timeframe_id"),)
