from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from trader.models.base import Base


class AssetType(Base):
    __tablename__ = "asset_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to many
    assets = relationship("Asset", lazy=True, backref=backref(__tablename__, lazy=False))


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    asset_type_id = Column(Integer, ForeignKey("asset_type.id"), nullable=False)
    name = Column(String, nullable=True)
    symbol = Column(String, nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # One to one
    cryptocurrency = relationship(
        "Cryptocurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )
    enabled_quote_asset = relationship(
        "EnabledQuoteAsset", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )
    standard_currency = relationship(
        "StandardCurrency", lazy=False, backref=backref(__tablename__, lazy=False), uselist=False
    )

    # One to many
    base_entry_implementations = relationship(
        "EntryImplementation", lazy=True, backref=backref(f"base_{__tablename__}", lazy=False)
    )
    positions = relationship("Position", lazy=True, backref=backref(__tablename__, lazy=False))

    # Many to many
    asset_tags = relationship("AssetXAssetTag", lazy=True, back_populates=__tablename__)

    __table_args__ = (UniqueConstraint("asset_type_id", "symbol"),)


class AssetTag(Base):
    __tablename__ = "asset_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    tag = Column(String, nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    assets = relationship("AssetXAssetTag", lazy=True, back_populates=__tablename__)


class AssetXAssetTag(Base):
    __tablename__ = "asset_x_asset_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    asset_tag_id = Column(Integer, ForeignKey("asset_tag.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many to many
    asset = relationship("Asset", lazy=False, back_populates="asset_tags")
    asset_tag = relationship("AssetTag", lazy=False, back_populates="assets")

    __table_args__ = (UniqueConstraint("asset_id", "asset_tag_id"),)
