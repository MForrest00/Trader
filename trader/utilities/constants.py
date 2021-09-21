from dataclasses import dataclass
import os
import pathlib
from typing import Any, Dict, Tuple
from trader.data.base import TIMEFRAME_ONE_DAY, TimeframeData
from trader.strategies.base import Strategy
from trader.strategies.entry.currency_ohlcv.bollinger_bands import BollingerBandsCurrencyOHLCVEntryStrategy
from trader.strategies.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossCurrencyOHLCVExitStrategy


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]


US_DOLLAR_SYMBOL = "USD"


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
class EnabledQuoteCurrency:
    symbol: str
    priority: int


INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES = (EnabledQuoteCurrency("USD", 1),)

INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES = (EnabledQuoteCurrency("USDC", 1), EnabledQuoteCurrency("USDT", 2))


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
