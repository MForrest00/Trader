from trader.models.asset import Asset
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.tasks import app


@app.task
def run_asset_ohlcv_implementations(
    source: Source,
    base_asset: Asset,
    quote_asset: Asset,
    timeframe: Timeframe,
):
    ...
