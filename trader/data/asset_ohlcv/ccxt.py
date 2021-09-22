from abc import abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
import ccxt
from ccxt.base.exchange import Exchange
from trader.data.asset_ohlcv import AssetOHLCVDataFeedRetriever
from trader.data.base import ASSET_TYPE_CRYPTOCURRENCY
from trader.models.asset import Asset
from trader.models.timeframe import Timeframe
from trader.utilities.functions import (
    datetime_to_ms_timestamp,
    fetch_base_data_id,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_DELTA_FUNCTION,
)


class CCXTAssetOHLCVDataFeedRetriever(AssetOHLCVDataFeedRetriever):
    def __init__(
        self,
        base_asset: Asset,
        quote_asset: Asset,
        timeframe: Timeframe,
        from_inclusive: datetime,
        to_exclusive: Optional[datetime] = None,
    ):
        super().__init__(base_asset, quote_asset, timeframe, from_inclusive, to_exclusive=to_exclusive)
        self._exchange = None

    @property
    @abstractmethod
    def CCXT_EXCHANGE_ID(self) -> str:
        ...

    @property
    def exchange(self) -> Exchange:
        if self._exchange is None:
            exchange_class = getattr(ccxt, self.CCXT_EXCHANGE_ID)
            self._exchange = exchange_class()
        return self._exchange

    def get_to_exclusive(self, to_exclusive: Optional[datetime]) -> datetime:
        return min(to_exclusive, datetime.now(timezone.utc)) if to_exclusive else datetime.now(timezone.utc)

    def validate_attributes(self) -> bool:
        if self.base_asset.asset_type_id != fetch_base_data_id(ASSET_TYPE_CRYPTOCURRENCY):
            raise ValueError("Base asset must be a cryptocurrency")
        if not self.from_inclusive < self.to_exclusive:
            raise ValueError("From inclusive value must be less than the to exclusive value")
        return True

    def retrieve_asset_ohlcv(self) -> List[Dict[str, Optional[Union[datetime, int, float]]]]:
        symbol = f"{self.base_asset.symbol}/{self.quote_asset.symbol}"
        since = datetime_to_ms_timestamp(self.from_inclusive)
        end = datetime_to_ms_timestamp(self.to_exclusive)
        output: List[Dict[str, Union[datetime, float]]] = []
        while since < end:
            data = self.exchange.fetch_ohlcv(symbol, timeframe=self.timeframe.ccxt_label, since=since)
            if len(data) == 0:
                since = datetime_to_ms_timestamp(
                    max(
                        since + TIMEFRAME_UNIT_TO_DELTA_FUNCTION[self.timeframe.unit](self.timeframe.amount),
                        since + TIMEFRAME_UNIT_TO_DELTA_FUNCTION["d"](1),
                    )
                )
            else:
                for record in data:
                    if record[0] >= end:
                        break
                    output.append(
                        {
                            "date_open": ms_timestamp_to_datetime(record[0]),
                            "open": record[1],
                            "high": record[2],
                            "low": record[3],
                            "close": record[4],
                            "volume": record[5],
                        }
                    )
                else:
                    since = datetime_to_ms_timestamp(
                        ms_timestamp_to_datetime(data[-1][0])
                        + TIMEFRAME_UNIT_TO_DELTA_FUNCTION[self.timeframe.unit](self.timeframe.amount)
                    )
                    continue
                break
        return output
