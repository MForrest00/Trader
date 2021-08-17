from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.persistence.models.base import Base


class CurrencyPlatform(Base):
    __tablename__ = "currency_platform"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("Currency", lazy=True, backref=backref("currency_platform", lazy=True))

    __table_args__ = (UniqueConstraint("name", "symbol", name=f"uc_{__tablename__}_name_symbol"),)


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    name = Column(String(250), nullable=False)
    symbol = Column(String(25), nullable=False)
    is_cryptocurrency = Column(Boolean, nullable=False, default=True)
    max_supply = Column(Numeric(33, 15), nullable=True)
    source_date_added = Column(DateTime, nullable=True)
    currency_platform_id = Column(Integer, ForeignKey("currency_platform.id"), nullable=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency_tags = relationship("CurrencyCurrencyTag", lazy=True, back_populates="currency")

    __table_args__ = (
        UniqueConstraint(
            "name", "symbol", "is_cryptocurrency", name=f"uc_{__tablename__}_name_symbol_is_cryptocurrency"
        ),
    )


class CurrencyTag(Base):
    __tablename__ = "currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    tag = Column(String(250), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currencies = relationship("CurrencyCurrencyTag", lazy=True, back_populates="currency_tag")


class CurrencyCurrencyTag(Base):
    __tablename__ = "currency_currency_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    currency_tag_id = Column(Integer, ForeignKey("currency_tag.id"), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    currency = relationship("Currency", lazy=True, back_populates="currency_tags")
    currency_tag = relationship("CurrencyTag", lazy=True, back_populates="currencies")

    __table_args__ = (
        UniqueConstraint("currency_id", "currency_tag_id", name=f"uc_{__tablename__}_currency_id_currency_tag_id"),
    )
