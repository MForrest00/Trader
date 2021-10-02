from trader.models.asset import Asset
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.tasks import app
from trader.utilities.functions.asset_ohlcv_implementation import dataframe_is_valid, fetch_asset_ohlcv_dataframe


@app.task
def run_implementations(
    source: Source,
    base_asset: Asset,
    quote_asset: Asset,
    timeframe: Timeframe,
):
    asset_ohlcv_dataframe = fetch_asset_ohlcv_dataframe(source, base_asset, quote_asset, timeframe)
    is_valid = dataframe_is_valid(asset_ohlcv_dataframe, timeframe)
    if not is_valid:
        raise Exception("Invalid values available for buy signal dataframe")
