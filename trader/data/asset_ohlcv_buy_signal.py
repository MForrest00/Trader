from datetime import datetime
from typing import Optional
from trader.models.asset import Asset
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.utilities.functions.asset_ohlcv import dataframe_is_valid, fetch_asset_ohlcv_as_dataframe


def generate_asset_ohlcv_buy_signals(
    source: Source,
    base_asset: Asset,
    quote_asset: Asset,
    timeframe: Timeframe,
    from_inclusive: Optional[datetime] = None,
    to_exclusive: Optional[datetime] = None,
):
    asset_ohlcv_dataframe = fetch_asset_ohlcv_as_dataframe(
        source, base_asset, quote_asset, timeframe, from_inclusive=from_inclusive, to_exclusive=to_exclusive
    )
    is_valid = dataframe_is_valid(asset_ohlcv_dataframe, timeframe)
    if not is_valid:
        raise Exception("Invalid values available for buy signal dataframe")
