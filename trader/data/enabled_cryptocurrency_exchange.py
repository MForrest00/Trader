from trader.connections.database import DBSession
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.source import Source
from trader.utilities.constants import INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGE_SOURCE_NAMES


def set_initial_enabled_cryptocurrency_exchanges() -> None:
    with DBSession() as session:
        for cryptocurrency_exchange_source_name in INITIAL_ENABLED_CRYPTOCURRENCY_EXCHANGE_SOURCE_NAMES:
            cryptocurrency_exchange = (
                session.query(CryptocurrencyExchange)
                .join(Source)
                .filter(Source.name == cryptocurrency_exchange_source_name)
                .one_or_none()
            )
            if cryptocurrency_exchange:
                if not cryptocurrency_exchange.enabled_cryptocurrency_exchange:
                    enabled_cryptocurrency_exchange = EnabledCryptocurrencyExchange(
                        cryptocurrency_exchange_id=cryptocurrency_exchange.id
                    )
                    session.add(enabled_cryptocurrency_exchange)
        session.commit()
