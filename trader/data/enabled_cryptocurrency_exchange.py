from trader.connections.database import session
from trader.data.initial.user import USER_ADMIN
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.enabled_cryptocurrency_exchange import (
    EnabledCryptocurrencyExchange,
    EnabledCryptocurrencyExchangeHistory,
)
from trader.models.source import Source
from trader.utilities.initial_enabled_data import INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES


def set_initial_enabled_cryptocurrency_exchanges() -> None:
    admin_id = USER_ADMIN.fetch_id()
    for item in INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES:
        cryptocurrency_exchange = (
            session.query(CryptocurrencyExchange).join(Source).filter(Source.name == item.source_name).one_or_none()
        )
        if cryptocurrency_exchange:
            if not cryptocurrency_exchange.enabled_cryptocurrency_exchange:
                enabled_cryptocurrency_exchange = EnabledCryptocurrencyExchange(
                    cryptocurrency_exchange_id=cryptocurrency_exchange.id
                )
                session.add(enabled_cryptocurrency_exchange)
                session.flush()
                enabled_cryptocurrency_exchange_history = EnabledCryptocurrencyExchangeHistory(
                    enabled_cryptocurrency_exchange_id=enabled_cryptocurrency_exchange.id,
                    user_id=admin_id,
                    priority=item.priority,
                )
                session.add(enabled_cryptocurrency_exchange_history)
    session.commit()
