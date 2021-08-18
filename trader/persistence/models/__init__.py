from trader.connections.database import database
from trader.persistence.models.base import Base
from trader.persistence.models.cryptocurrency import *
from trader.persistence.models.cryptocurrency_exchange import *
from trader.persistence.models.cryptocurrency_exchange_rank import *
from trader.persistence.models.cryptocurrency_rank import *
from trader.persistence.models.currency import *
from trader.persistence.models.currency_ohlcv import *
from trader.persistence.models.google_trends import *
from trader.persistence.models.source import *
from trader.persistence.models.timeframe import *


def initialize_models() -> None:
    Base.metadata.create_all(database)
