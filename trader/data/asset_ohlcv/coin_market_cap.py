from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode
import requests
from trader.data.initial.asset_type import ASSET_TYPE_CRYPTOCURRENCY, ASSET_TYPE_STANDARD_CURRENCY
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.data.asset_ohlcv import AssetOHLCVDataFeedRetriever
from trader.utilities.constants import US_DOLLAR_SYMBOL
from trader.utilities.functions import iso_time_string_to_datetime


class CoinMarketCapAssetOHLCVDataFeedRetriever(AssetOHLCVDataFeedRetriever):
    SOURCE = SOURCE_COIN_MARKET_CAP

    def get_to_exclusive(self, to_exclusive: Optional[datetime]) -> datetime:
        temporary_to_exclusive = (
            min(to_exclusive, datetime.now(timezone.utc)) if to_exclusive else datetime.now(timezone.utc)
        )
        return temporary_to_exclusive - timedelta(days=1)

    def validate_attributes(self) -> bool:
        if self.base_asset.source_id != self.source_id:
            raise ValueError("Base asset must be from source CoinMarketCap")
        if self.base_asset.asset_type_id != ASSET_TYPE_CRYPTOCURRENCY.fetch_id():
            raise ValueError("Base asset must be a cryptocurrency")
        if self.base_asset.cryptocurrency.source_entity_id is None:
            raise ValueError("Base asset must have a source_entity_id attribute")
        if (
            self.quote_asset.symbol != US_DOLLAR_SYMBOL
            or self.quote_asset.asset_type_id != ASSET_TYPE_STANDARD_CURRENCY.fetch_id()
        ):
            raise ValueError("Quote asset must be standard currency USD")
        if self.timeframe.id != TIMEFRAME_ONE_DAY.fetch_id():
            raise ValueError("Timeframe must be one day")
        if not self.from_inclusive < self.to_exclusive:
            raise ValueError("From inclusive value must be less than the to exclusive value")
        return True

    def retrieve_asset_ohlcv(self) -> List[Dict[str, Optional[Union[datetime, int, float]]]]:
        from_timestamp = int(self.from_inclusive.timestamp())
        to_timestamp = int(self.to_exclusive.timestamp())
        query_string = urlencode(
            {
                "id": self.base_asset.cryptocurrency.source_entity_id,
                "convertId": 2781,
                "timeStart": from_timestamp,
                "timeEnd": to_timestamp,
            }
        )
        response = requests.get(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?{query_string}")
        data = response.json()
        output: List[Dict[str, Union[datetime, float]]] = []
        for record in data["data"]["quotes"]:
            try:
                date_high = iso_time_string_to_datetime(record["timeHigh"]) if "timeHigh" in record else None
            except ValueError:
                date_high = None
            try:
                date_low = iso_time_string_to_datetime(record["timeLow"]) if "timeLow" in record else None
            except ValueError:
                date_low = None
            output.append(
                {
                    "date_open": iso_time_string_to_datetime(record["timeOpen"]),
                    "open": record["quote"]["open"],
                    "high": record["quote"]["high"],
                    "low": record["quote"]["low"],
                    "close": record["quote"]["close"],
                    "volume": record["quote"]["volume"],
                    "date_high": date_high,
                    "date_low": date_low,
                }
            )
        return output
