from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledQuoteAsset(Base):
    __tablename__ = "enabled_quote_asset"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    history = relationship(
        "EnabledQuoteAssetHistory",
        lazy=False,
        order_by="desc(EnabledQuoteAssetHistory.date_created)",
        backref=backref(__tablename__, lazy=False),
    )


class EnabledQuoteAssetHistory(Base):
    __tablename__ = "enabled_quote_asset_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enabled_quote_asset_id = Column(Integer, ForeignKey("enabled_quote_asset.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    priority = Column(SmallInteger, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
