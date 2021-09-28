from dataclasses import dataclass
import os
import pathlib
from typing import Any, Dict, Tuple
from trader.data.initial.asset_type import ASSET_TYPE_CRYPTOCURRENCY, ASSET_TYPE_STANDARD_CURRENCY, AssetTypeData
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY, TimeframeData
from trader.strategies.base import Strategy
from trader.strategies.entry.asset_ohlcv.bollinger_bands import BollingerBandsAssetOHLCVEntryStrategy
from trader.strategies.exit.asset_ohlcv.trailing_stop_loss import TrailingStopLossAssetOHLCVExitStrategy


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]


US_DOLLAR_SYMBOL = "USD"


DATA_FEED_MONITOR_KEY = "data_feed_monitor"
DATA_FEED_MESSAGE_DELIMITER = ":"


@dataclass
class EnabledCryptocurrencyExchange:
    source_name: str
    priority: int


INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES = (
    EnabledCryptocurrencyExchange("Binance.US", 6),
    EnabledCryptocurrencyExchange("Bittrex", 7),
    EnabledCryptocurrencyExchange("CEX.IO", 8),
    EnabledCryptocurrencyExchange("Coinbase Exchange", 1),
    EnabledCryptocurrencyExchange("Crypto.com Exchange", 9),
    EnabledCryptocurrencyExchange("FTX US", 5),
    EnabledCryptocurrencyExchange("Gate.io", 10),
    EnabledCryptocurrencyExchange("Gemini", 4),
    EnabledCryptocurrencyExchange("Kraken", 2),
    EnabledCryptocurrencyExchange("Poloniex", 3),
)


@dataclass
class EnabledQuoteAsset:
    asset_type: AssetTypeData
    symbol: str
    priority: int


INITIAL_ENABLED_QUOTE_ASSETS = (
    EnabledQuoteAsset(ASSET_TYPE_STANDARD_CURRENCY, US_DOLLAR_SYMBOL, 1),
    EnabledQuoteAsset(ASSET_TYPE_CRYPTOCURRENCY, "USDC", 2),
    EnabledQuoteAsset(ASSET_TYPE_CRYPTOCURRENCY, "USDT", 3),
)


@dataclass
class EnabledStrategyVersionInstance:
    strategy: Strategy
    arguments: Dict[str, Any]
    priority: int


INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES: Dict[TimeframeData, Tuple[EnabledStrategyVersionInstance, ...]] = {
    TIMEFRAME_ONE_DAY: (
        EnabledStrategyVersionInstance(BollingerBandsAssetOHLCVEntryStrategy, {"bollinger_bands_period": 20}, 1),
    ),
}

INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES: Dict[TimeframeData, Tuple[EnabledStrategyVersionInstance, ...]] = {
    TIMEFRAME_ONE_DAY: (
        EnabledStrategyVersionInstance(
            TrailingStopLossAssetOHLCVExitStrategy, {"trailing_stop_loss_percentage": 0.1}, 1
        ),
    ),
}
