import os
import pathlib
import sys


sys.path.append(os.path.split(pathlib.Path(__file__).parent.absolute())[0])


from trader.data.initial import initialize_data
from trader.data.enabled_cryptocurrency_exchange import set_initial_enabled_cryptocurrency_exchanges
from trader.data.enabled_quote_asset import set_initial_enabled_quote_assets
from trader.data.enabled_strategy_version_instance import set_initial_enabled_strategy_version_instances
from trader.models import initialize_models
from trader.models.views import initialize_views
from trader.strategies import initialize_strategies
from trader.tasks.asset_ohlcv import queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap
from trader.tasks.country import update_countries_from_iso
from trader.tasks.cryptocurrency_exchange_market_stat import (
    queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.tasks.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.tasks.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.tasks.standard_currency import update_standard_currencies_from_iso
from trader.utilities.logging import logger


def main():
    logger.debug("Initializing tables, views, and base data")
    initialize_models()
    initialize_views()
    initialize_data()
    logger.debug("Loading ISO countries")
    update_countries_from_iso.apply()
    logger.debug("Loading ISO standard currencies")
    update_standard_currencies_from_iso.apply()
    logger.debug("Loading CoinMarketCap cryptocurrency exchange ranks")
    update_cryptocurrency_exchange_ranks_from_coin_market_cap.apply()
    set_initial_enabled_cryptocurrency_exchanges()
    logger.debug("Loading current CoinMarketCap cryptocurrency ranks")
    update_current_cryptocurrency_ranks_from_coin_market_cap.apply(kwargs={"limit": 5000})
    set_initial_enabled_quote_assets()
    initialize_strategies()
    set_initial_enabled_strategy_version_instances()
    queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap.apply(kwargs={"synchronous": True})
    queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap.delay()


if __name__ == "__main__":
    main()
