from trader.data.base import DATA_FEED_ASSET_OHLCV
from trader.strategies.base import Strategy


class AssetOHLCVStrategy(Strategy):
    BASE_DATA_FEED = DATA_FEED_ASSET_OHLCV
