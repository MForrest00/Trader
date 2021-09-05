import os
import pathlib


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

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
