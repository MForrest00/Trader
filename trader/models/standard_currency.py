from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from trader.models.base import Base


class StandardCurrency(Base):
    __tablename__ = "standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    minor_unit = Column(Integer, nullable=True)

    # Many to many
    cryptocurrency_exchanges = relationship(
        "CryptocurrencyExchangeXStandardCurrency", lazy=True, back_populates=__tablename__
    )
