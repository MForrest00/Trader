from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from trader.models.base import Base


class StandardCurrency(Base):
    __tablename__ = "standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    minor_unit = Column(Integer, nullable=True)
