import os
import pathlib
import sys


sys.path.append(os.path.split(pathlib.Path(__file__).parent.absolute())[0])


from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import CRYPTOCURRENCY, CRYPTOCURRENCY_EXCHANGE, initialize_base_data, ONE_DAY, WEB_SEARCH, WORLDWIDE
from trader.data.country import update_countries_from_iso
from trader.data.cryptocurrency_exchange_market_stat import (
    update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.data.currency_ohlcv import update_daily_usd_ohlcv_from_coin_market_cap
from trader.data.google_trends import update_interest_over_time_from_google_trends
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.models import initialize_models
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.currency import Currency
from trader.models.google_trends import GoogleTrendsPullGeo, GoogleTrendsPullGprop
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.models.views import initialize_views


def main():
    initialize_models()
    initialize_base_data()
    initialize_views()
    update_countries_from_iso()
    update_standard_currencies_from_iso()
    update_cryptocurrency_exchange_ranks_from_coin_market_cap()
    update_current_cryptocurrency_ranks_from_coin_market_cap()
    month_start_six_months_ago = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ) - relativedelta(months=6)
    one_day_id = int(cache.get(ONE_DAY.cache_key).decode())
    web_search_id = int(cache.get(WEB_SEARCH.cache_key).decode())
    worldwide_id = int(cache.get(WORLDWIDE.cache_key).decode())
    with DBSession() as session:
        one_day = session.query(Timeframe).get(one_day_id)
        web_search = session.query(GoogleTrendsPullGprop).get(web_search_id)
        worldwide = session.query(GoogleTrendsPullGeo).get(worldwide_id)
    update_interest_over_time_from_google_trends(
        ["bitcoin"], worldwide, web_search, one_day, month_start_six_months_ago
    )
    cryptocurrency_exchange_id = int(cache.get(CRYPTOCURRENCY_EXCHANGE.cache_key).decode())
    with DBSession() as session:
        binance = (
            session.query(CryptocurrencyExchange)
            .join(Source)
            .filter(Source.name == "Binance", Source.source_type_id == cryptocurrency_exchange_id)
            .one_or_none()
        )
    if binance:
        update_cryptocurrency_exchange_market_stats_from_coin_market_cap(binance)
    cryptocurrency_id = int(cache.get(CRYPTOCURRENCY.cache_key).decode())
    with DBSession() as session:
        bitcoin = session.query(Currency).filter_by(symbol="BTC", currency_type_id=cryptocurrency_id).one_or_none()
    if bitcoin:
        update_daily_usd_ohlcv_from_coin_market_cap(bitcoin, month_start_six_months_ago)


if __name__ == "__main__":
    main()
