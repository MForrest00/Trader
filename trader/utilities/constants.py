import os
import pathlib


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGE_SOURCE_NAMES_PRIORITY = (
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

INITIAL_ENABLED_QUOTE_STANDARD_CURRENCY_SYMBOLS_PRIORITY = (("USD", 1),)

INITIAL_ENABLED_QUOTE_CRYPTOCURRENCY_SYMBOLS_PRIORITY = (("USDC", 1), ("USDT", 2))
