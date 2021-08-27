from trader.connections.database import DBSession
from trader.models.views.cryptocurrency import CRYPTOCURRENCY_SQL, CRYPTOCURRENCY_PARAMS
from trader.models.views.standard_currency import STANDARD_CURRENCY_SQL, STANDARD_CURRENCY_PARAMS


def initialize_views() -> None:
    with DBSession() as session:
        session.execute(CRYPTOCURRENCY_SQL, CRYPTOCURRENCY_PARAMS)
        session.execute(STANDARD_CURRENCY_SQL, STANDARD_CURRENCY_PARAMS)
        session.commit()
