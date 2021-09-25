from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from trader.data.initial.base import BaseData
from trader.data.initial.source_type import (
    SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA,
    SOURCE_TYPE_MISCELLANEOUS_DATA,
    SOURCE_TYPE_SEARCH_DATA,
    SourceTypeData,
)
from trader.models.source import Source


@dataclass(frozen=True, eq=True)
class SourceData(BaseData):
    source_id: Optional[int]
    source_type: SourceTypeData
    name: str
    url: Optional[str] = None

    def query_instance(self, session: Session) -> Optional[Source]:
        return session.query(Source).filter_by(source_type_id=self.source_type.fetch_id(), name=self.name).one_or_none()

    def create_instance(self) -> Source:
        return Source(
            source_id=self.source_id, source_type_id=self.source_type.fetch_id(), name=self.name, url=self.url
        )


SOURCE_ISO = SourceData("source_iso_id", None, "ISO", SOURCE_TYPE_MISCELLANEOUS_DATA, url="https://www.iso.org/")
SOURCE_COIN_MARKET_CAP = SourceData(
    "source_coin_market_cap_id",
    None,
    "CoinMarketCap",
    SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA,
    url="https://coinmarketcap.com/",
)
SOURCE_COIN_GECKO = SourceData(
    "source_coin_gecko_id", None, "CoinGecko", SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA, url="https://www.coingecko.com/"
)
SOURCE_GOOGLE_TRENDS = SourceData(
    "source_google_trends_id", None, "Google Trends", SOURCE_TYPE_SEARCH_DATA, url="https://trends.google.com/"
)
SOURCES = (SOURCE_ISO, SOURCE_COIN_MARKET_CAP, SOURCE_COIN_GECKO, SOURCE_GOOGLE_TRENDS)
