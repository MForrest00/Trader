from dataclasses import dataclass
from typing import Optional
from trader.connections.database import session
from trader.data.initial.base import BaseData
from trader.models.source import SourceType


@dataclass(frozen=True, eq=True)
class SourceTypeData(BaseData):
    description: str

    def query_instance(self) -> Optional[SourceType]:
        return session.query(SourceType).filter_by(description=self.description).one_or_none()

    def create_instance(self) -> SourceType:
        return SourceType(description=self.description)


SOURCE_TYPE_MISCELLANEOUS_DATA = SourceTypeData("source_type_miscellaneous_data_id", "Miscellaneous data")
SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA = SourceTypeData(
    "source_type_cryptocurrency_market_data_id", "Cryptocurrency market data"
)
SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE = SourceTypeData(
    "source_type_cryptocurrency_exchange_id", "Cryptocurrency exchange"
)
SOURCE_TYPE_SEARCH_DATA = SourceTypeData("source_type_search_data_id", "Search data")
SOURCE_TYPES = (
    SOURCE_TYPE_MISCELLANEOUS_DATA,
    SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA,
    SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE,
    SOURCE_TYPE_SEARCH_DATA,
)
