from trader.connections.database import database
from trader.models.base import Base
from trader.models.country import *
from trader.models.cryptocurrency import *
from trader.models.cryptocurrency_exchange import *
from trader.models.cryptocurrency_exchange_market import *
from trader.models.cryptocurrency_exchange_market_stat import *
from trader.models.cryptocurrency_exchange_rank import *
from trader.models.cryptocurrency_rank import *
from trader.models.currency import *
from trader.models.currency_ohlcv import *
from trader.models.google_trends import *
from trader.models.source import *
from trader.models.standard_currency import *
from trader.models.timeframe import *


def initialize_models() -> None:
    Base.metadata.create_all(database)
