from dataclasses import dataclass
from typing import Optional
from trader.connections.database import session
from trader.data.initial.base import BaseData
from trader.models.asset import AssetType


@dataclass(frozen=True, eq=True)
class AssetTypeData(BaseData):
    description: str

    def query_instance(self) -> Optional[AssetType]:
        return session.query(AssetType).filter_by(description=self.description).one_or_none()

    def create_instance(self) -> AssetType:
        return AssetType(description=self.description)


ASSET_TYPE_UNKNOWN_CURRENCY = AssetTypeData("asset_type_unknown_currency_id", "Unknown currency")
ASSET_TYPE_STANDARD_CURRENCY = AssetTypeData("asset_type_standard_currency_id", "Standard currency")
ASSET_TYPE_CRYPTOCURRENCY = AssetTypeData("asset_type_cryptocurrency_id", "Cryptocurrency")
ASSET_TYPES = (ASSET_TYPE_UNKNOWN_CURRENCY, ASSET_TYPE_STANDARD_CURRENCY, ASSET_TYPE_CRYPTOCURRENCY)
