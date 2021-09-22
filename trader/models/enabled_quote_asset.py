from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledQuoteAsset(Base):
    __tablename__ = "enabled_quote_asset"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, unique=True)
    priority = Column(SmallInteger, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)
    date_enabled = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
