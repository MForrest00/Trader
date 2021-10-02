from dataclasses import dataclass
from typing import Optional
from trader.connections.database import session
from trader.data.initial.base import BaseData
from trader.models.data_feed import DataFeed


@dataclass(frozen=True, eq=True)
class DataFeedData(BaseData):
    name: str

    def query_instance(self) -> Optional[DataFeed]:
        return session.query(DataFeed).filter_by(name=self.name).one_or_none()

    def create_instance(self) -> DataFeed:
        return DataFeed(name=self.name)


DATA_FEED_ASSET_OHLCV = DataFeedData("data_feed_asset_ohlcv_id", "Asset OHLCV")
DATA_FEED_GOOGLE_TRENDS_ASSET_NAME = DataFeedData("data_feed_google_trends_asset_name_id", "Google trends asset name")
DATA_FEEDS = (DATA_FEED_ASSET_OHLCV, DATA_FEED_GOOGLE_TRENDS_ASSET_NAME)
