from trader.connections.database import session
from trader.models.views.asset_ohlcv import ASSET_OHLCV_SQL
from trader.models.views.cryptocurrency import CRYPTOCURRENCY_SQL
from trader.models.views.cryptocurrency_exchange import CRYPTOCURRENCY_EXCHANGE_SQL
from trader.models.views.cryptocurrency_exchange_market import CRYPTOCURRENCY_EXCHANGE_MARKET_SQL
from trader.models.views.google_trends import GOOGLE_TRENDS_SQL
from trader.models.views.standard_currency import STANDARD_CURRENCY_SQL


def initialize_views() -> None:
    session.execute(ASSET_OHLCV_SQL)
    session.execute(CRYPTOCURRENCY_SQL)
    session.execute(CRYPTOCURRENCY_EXCHANGE_SQL)
    session.execute(CRYPTOCURRENCY_EXCHANGE_MARKET_SQL)
    session.execute(GOOGLE_TRENDS_SQL)
    session.execute(STANDARD_CURRENCY_SQL)
    session.commit()
