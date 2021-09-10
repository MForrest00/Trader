from trader.implementations.currency.currency_ohlcv.base import CurrencyOHLCVImplementation
from trader.strategies.currency.entrance.currency_ohlcv.bollinger_bands import (
    BollingerBandsEntranceCurrencyOHLCVStrategy,
)
from trader.strategies.currency.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossExitCurrencyOHLCVStrategy


class BollingerBandsTrailingStopLossCurrencyOHLCVImplementation(CurrencyOHLCVImplementation):
    NAME = "Bollinger Bands with Trailing Stop Loss"
    VERSION = "1.0.0"
    ENTRANCE_STRATEGIES = (BollingerBandsEntranceCurrencyOHLCVStrategy,)
    EXIT_STRATEGIES = (TrailingStopLossExitCurrencyOHLCVStrategy,)
