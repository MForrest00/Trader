from datetime import datetime
from typing import Optional
from trader.models.cryptocurrency import Cryptocurrency
from trader.models.currency import Currency
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.utilities.functions.currency_ohlcv import dataframe_is_valid, fetch_currency_ohlcv_as_dataframe


def generate_buy_signals(
    source: Source,
    base_currency: Cryptocurrency,
    quote_currency: Currency,
    timeframe: Timeframe,
    from_inclusive: Optional[datetime] = None,
    to_exclusive: Optional[datetime] = None,
):
    dataframe = fetch_currency_ohlcv_as_dataframe(
        source, base_currency, quote_currency, timeframe, from_inclusive=from_inclusive, to_exclusive=to_exclusive
    )
    is_valid = dataframe_is_valid(dataframe, timeframe)
    if not is_valid:
        raise Exception("Invalid values available for buy signal dataframe")
