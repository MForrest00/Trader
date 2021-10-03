from trader.connections.database import session
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.source import Source
from trader.utilities.initial_enabled_data import INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES


def set_initial_enabled_cryptocurrency_exchanges() -> None:
    for enabled_cryptocurrency_exchange in INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGES:
        cryptocurrency_exchange = (
            session.query(CryptocurrencyExchange)
            .join(Source)
            .filter(Source.name == enabled_cryptocurrency_exchange.source_name)
            .one_or_none()
        )
        if cryptocurrency_exchange:
            if not cryptocurrency_exchange.enabled_cryptocurrency_exchange:
                enabled_cryptocurrency_exchange = EnabledCryptocurrencyExchange(
                    cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                    priority=enabled_cryptocurrency_exchange.priority,
                )
                session.add(enabled_cryptocurrency_exchange)
    session.commit()
