from dataclasses import dataclass
import os
import pathlib
from typing import Any, Dict, Tuple
from trader.data.base import TIMEFRAME_ONE_DAY, TimeframeData
from trader.strategies.base import Strategy
from trader.strategies.entry.currency_ohlcv.bollinger_bands import BollingerBandsCurrencyOHLCVEntryStrategy
from trader.strategies.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossCurrencyOHLCVExitStrategy


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES = (
    ("Binance.US", 6),
    ("Bittrex", 7),
    ("CEX.IO", 8),
    ("Coinbase Exchange", 1),
    ("Crypto.com Exchange", 9),
    ("FTX US", 5),
    ("Gate.io", 10),
    ("Gemini", 4),
    ("Kraken", 2),
    ("Poloniex", 3),
)

INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES = (("USD", 1),)

INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES = (("USDC", 1), ("USDT", 2))


@dataclass
class EnabledStrategyVersionInstance:
    strategy: Strategy
    arguments: Dict[str, Any]
    priority: int


INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES: Dict[TimeframeData, Tuple[EnabledStrategyVersionInstance, ...]] = {
    TIMEFRAME_ONE_DAY: (
        EnabledStrategyVersionInstance(BollingerBandsCurrencyOHLCVEntryStrategy, {"bollinger_bands_period": 20}, 1),
    ),
}

INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES: Dict[TimeframeData, Tuple[EnabledStrategyVersionInstance, ...]] = {
    TIMEFRAME_ONE_DAY: (
        EnabledStrategyVersionInstance(
            TrailingStopLossCurrencyOHLCVExitStrategy, {"trailing_stop_loss_percentage": 0.1}, 1
        ),
    ),
}
