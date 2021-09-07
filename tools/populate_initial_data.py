import os
import pathlib
import sys


sys.path.append(os.path.split(pathlib.Path(__file__).parent.absolute())[0])


from trader.connections.database import DBSession
from trader.data.base import initialize_base_data
from trader.data.country import update_countries_from_iso
from trader.data.cryptocurrency_exchange_market_stat import (
    update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.data.currency_ohlcv import update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap
from trader.data.enabled_cryptocurrency_exchange import set_initial_enabled_cryptocurrency_exchanges
from trader.data.enabled_quote_currency import set_initial_enabled_quote_currencies
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.models import initialize_models
from trader.models.currency import Currency
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.views import initialize_views
from trader.strategies import initialize_strategies
from trader.utilities.functions.cryptocurrency_exchange import (
    fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges,
)
from trader.utilities.logging import logger


def main():
    logger.debug("Initializing tables, views, and base data")
    initialize_models()
    initialize_views()
    initialize_base_data()
    logger.debug("Loading ISO countries")
    update_countries_from_iso()
    logger.debug("Loading ISO standard currencies")
    update_standard_currencies_from_iso()
    logger.debug("Loading CoinMarketCap cryptocurrency exchange ranks")
    update_cryptocurrency_exchange_ranks_from_coin_market_cap()
    set_initial_enabled_cryptocurrency_exchanges()
    logger.debug("Loading current CoinMarketCap cryptocurrency ranks")
    update_current_cryptocurrency_ranks_from_coin_market_cap(5000)
    set_initial_enabled_quote_currencies()
    with DBSession() as session:
        enabled_cryptocurrency_exchanges = (
            session.query(EnabledCryptocurrencyExchange).filter_by(is_disabled=False).all()
        )
        for enabled_cryptocurrency_exchange in enabled_cryptocurrency_exchanges:
            logger.debug(
                "Loading CoinMarketCap cryptocurrency exchange market stats for exchange %s",
                enabled_cryptocurrency_exchange.cryptocurrency_exchange.source.name,
            )
            update_cryptocurrency_exchange_market_stats_from_coin_market_cap(
                enabled_cryptocurrency_exchange.cryptocurrency_exchange
            )
        base_currency_ids = fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges(
            session, (e.cryptocurrency_exchange for e in enabled_cryptocurrency_exchanges)
        )
        for base_currency_id in base_currency_ids:
            base_currency = session.query(Currency).get(base_currency_id)
            if base_currency:
                cryptocurrency = base_currency.cryptocurrency
                if cryptocurrency:
                    logger.debug(
                        "Loading CoinMarketCap cryptocurrency daily USD OHLCV for cryptocurrency %s", base_currency.name
                    )
                    update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(
                        cryptocurrency, cryptocurrency.source_date_added
                    )
    initialize_strategies()


if __name__ == "__main__":
    main()
