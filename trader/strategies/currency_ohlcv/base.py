from trader.data.base import DATA_FEED_CURRENCY_OHLCV
from trader.strategies.base import Strategy


class CurrencyOHLCVStrategy(Strategy):
    BASE_DATA_FEED = DATA_FEED_CURRENCY_OHLCV
