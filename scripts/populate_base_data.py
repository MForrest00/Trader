import os
import pathlib
import sys


sys.path.append(os.path.split(pathlib.Path(__file__).parent.absolute())[0])


from trader.connections.database import DBSession
from trader.data.base import (
    CRYPTOCURRENCY,
    CRYPTOCURRENCY_EXCHANGE,
    initialize_base_data,
    ONE_DAY,
    WEB_SEARCH,
    WORLDWIDE,
)
from trader.data.country import update_countries_from_iso
from trader.data.cryptocurrency_exchange_market_stat import (
    update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.data.currency_ohlcv import update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap
from trader.data.enabled_cryptocurrency_exchange import set_initial_enabled_cryptocurrency_exchanges
from trader.data.enabled_quote_currency import set_initial_enabled_quote_currencies
from trader.data.google_trends import update_interest_over_time_from_google_trends
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.models import initialize_models
from trader.models.cryptocurrency import Cryptocurrency
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.currency import Currency
from trader.models.google_trends import GoogleTrendsPullGeo, GoogleTrendsPullGprop
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.models.views import initialize_views
from trader.utilities.functions import fetch_base_data_id


def main():
    initialize_models()
    initialize_base_data()
    initialize_views()
    update_countries_from_iso()
    update_standard_currencies_from_iso()
    update_cryptocurrency_exchange_ranks_from_coin_market_cap()
    set_initial_enabled_cryptocurrency_exchanges()
    update_current_cryptocurrency_ranks_from_coin_market_cap()
    set_initial_enabled_quote_currencies()
    cryptocurrency_exchange_id = fetch_base_data_id(CRYPTOCURRENCY_EXCHANGE)
    with DBSession() as session:
        binance = (
            session.query(CryptocurrencyExchange)
            .join(Source)
            .filter(Source.name == "Binance", Source.source_type_id == cryptocurrency_exchange_id)
            .one_or_none()
        )
    if binance:
        update_cryptocurrency_exchange_market_stats_from_coin_market_cap(binance)
    cryptocurrency_id = fetch_base_data_id(CRYPTOCURRENCY)
    with DBSession() as session:
        bitcoin = (
            session.query(Cryptocurrency)
            .join(Currency)
            .filter(Currency.symbol == "BTC", Currency.currency_type_id == cryptocurrency_id)
            .one_or_none()
        )
    if bitcoin:
        update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(bitcoin, bitcoin.source_date_added)
        one_day_id = fetch_base_data_id(ONE_DAY)
        web_search_id = fetch_base_data_id(WEB_SEARCH)
        worldwide_id = fetch_base_data_id(WORLDWIDE)
        with DBSession() as session:
            one_day = session.query(Timeframe).get(one_day_id)
            web_search = session.query(GoogleTrendsPullGprop).get(web_search_id)
            worldwide = session.query(GoogleTrendsPullGeo).get(worldwide_id)
        update_interest_over_time_from_google_trends(
            [bitcoin.currency.name], worldwide, web_search, one_day, bitcoin.source_date_added
        )


if __name__ == "__main__":
    main()
