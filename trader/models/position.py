from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class Position(Base):
    __tablename__ = "position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    data = Column(JSONB, nullable=True)
    is_demo = Column(Boolean, nullable=False, default=False)
    date_opened = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_closed = Column(DateTime(timezone=True), nullable=True)

    # One to many
    exit_implementations = relationship("ExitImplementation", lazy=True, backref=backref(__tablename__, lazy=False))
    position_purchases = relationship("PositionPurchase", lazy=True, backref=backref(__tablename__, lazy=False))
    position_sales = relationship("PositionSale", lazy=True, backref=backref(__tablename__, lazy=False))


class PositionPurchase(Base):
    __tablename__ = "position_purchase"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    buy_signal_id = Column(Integer, ForeignKey("buy_signal.id"), nullable=False)
    price = Column(Numeric, nullable=False)
    size = Column(Numeric, nullable=False)
    fees = Column(Numeric, nullable=False)
    data = Column(JSONB, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class PositionSale(Base):
    __tablename__ = "position_sale"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    sell_signal_id = Column(Integer, ForeignKey("sell_signal.id"), nullable=False)
    price = Column(Numeric, nullable=False)
    size = Column(Numeric, nullable=False)
    fees = Column(Numeric, nullable=False)
    data = Column(JSONB, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
