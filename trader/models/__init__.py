from trader.connections.database import database
from trader.models.asset import *
from trader.models.asset_ohlcv import *
from trader.models.base import Base
from trader.models.buy_signal import *
from trader.models.country import *
from trader.models.cryptocurrency import *
from trader.models.cryptocurrency_exchange import *
from trader.models.cryptocurrency_exchange_market import *
from trader.models.cryptocurrency_exchange_market_stat import *
from trader.models.cryptocurrency_exchange_rank import *
from trader.models.cryptocurrency_rank import *
from trader.models.data_feed import *
from trader.models.enabled_cryptocurrency_exchange import *
from trader.models.enabled_quote_asset import *
from trader.models.enabled_strategy_version_instance import *
from trader.models.entry_implementation import *
from trader.models.exit_implementation import *
from trader.models.google_trends import *
from trader.models.position import *
from trader.models.sell_signal import *
from trader.models.source import *
from trader.models.standard_currency import *
from trader.models.strategy import *
from trader.models.timeframe import *
from trader.models.user import *


def initialize_models() -> None:
    Base.metadata.create_all(database)
