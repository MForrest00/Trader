from trader.connections.database import DBSession
from trader.models.views.cryptocurrency import CRYPTOCURRENCY_SQL
from trader.models.views.cryptocurrency_exchange import CRYPTOCURRENCY_EXCHANGE_SQL
from trader.models.views.cryptocurrency_exchange_market import CRYPTOCURRENCY_EXCHANGE_MARKET_SQL
from trader.models.views.currency_ohlcv import CURRENCY_OHLCV_SQL
from trader.models.views.google_trends import GOOGLE_TRENDS_SQL
from trader.models.views.standard_currency import STANDARD_CURRENCY_SQL


def initialize_views() -> None:
    with DBSession() as session:
        session.execute(CRYPTOCURRENCY_SQL)
        session.execute(CRYPTOCURRENCY_EXCHANGE_SQL)
        session.execute(CRYPTOCURRENCY_EXCHANGE_MARKET_SQL)
        session.execute(CURRENCY_OHLCV_SQL)
        session.execute(GOOGLE_TRENDS_SQL)
        session.execute(STANDARD_CURRENCY_SQL)
        session.commit()
