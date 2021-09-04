from datetime import datetime, timezone
import os
import pathlib
from trader.data.base import ONE_DAY, ONE_MINUTE, ONE_MONTH, EIGHT_MINUTE


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

CRYPTOCURRENCY_RANK_LIMIT = 500

GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE = datetime(2004, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_WEB_SEARCH_MINUTE_GRANULARITY_CUTOFF = datetime(2015, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE = datetime(2008, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_OTHER_SEARCH_MINUTE_GRANULARITY_CUTOFF = datetime(2017, 9, 12, tzinfo=timezone.utc)
GOOGLE_TRENDS_TIMEFRAME_RANKS = (
    ONE_MINUTE.base_label,
    EIGHT_MINUTE.base_label,
    ONE_DAY.base_label,
    ONE_MONTH.base_label,
)

INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGE_SOURCE_NAMES = (
    "Binance.US",
    "Bittrex",
    "CEX.IO",
    "Coinbase Exchange",
    "Crypto.com Exchange",
    "FTX US",
    "Gate.io",
    "Gemini",
    "Kraken",
    "Poloniex",
)

INITIAL_ENABLED_QUOTE_STANDARD_CURRENCY_SYMBOLS = ("USD",)

INITIAL_ENABLED_QUOTE_CRYPTOCURRENCY_SYMBOLS = ("USDC", "USDT")
