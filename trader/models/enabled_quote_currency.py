from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.sql import func
from trader.models.base import Base


class EnabledQuoteCurrency(Base):
    __tablename__ = "enabled_quote_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False, unique=True)
    is_disabled = Column(Boolean, nullable=False, default=False)
    date_enabled = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
