from trader.connections.database import DBSession
from trader.models.views.cryptocurrency import CRYPTOCURRENCY_SQL
from trader.models.views.standard_currency import STANDARD_CURRENCY_SQL


def initialize_views() -> None:
    with DBSession() as session:
        session.execute(CRYPTOCURRENCY_SQL)
        session.execute(STANDARD_CURRENCY_SQL)
        session.commit()
