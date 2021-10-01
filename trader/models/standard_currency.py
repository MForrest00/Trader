from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class StandardCurrency(Base):
    __tablename__ = "standard_currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, unique=True)
    iso_numeric_code = Column(String(3), nullable=False, unique=True)
    minor_unit = Column(Integer, nullable=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    countries = relationship("CountryXStandardCurrency", lazy=True, back_populates=__tablename__)
    cryptocurrency_exchanges = relationship(
        "CryptocurrencyExchangeXStandardCurrency", lazy=True, back_populates=__tablename__
    )
