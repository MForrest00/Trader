import os
import pathlib
import sys


sys.path.append(os.path.split(pathlib.Path(__file__).parent.absolute())[0])


from trader.connections.database import DBSession
from trader.data.asset_ohlcv.coin_market_cap import CoinMarketCapAssetOHLCVDataFeedRetriever
from trader.data.initial import initialize_data
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.data.country import update_countries_from_iso
from trader.data.cryptocurrency_exchange_market_stat import (
    update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.data.enabled_cryptocurrency_exchange import set_initial_enabled_cryptocurrency_exchanges
from trader.data.enabled_quote_asset import set_initial_enabled_quote_assets
from trader.data.enabled_strategy_version_instance import set_initial_enabled_strategy_version_instances
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.models import initialize_models
from trader.models.asset import Asset
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.timeframe import Timeframe
from trader.models.views import initialize_views
from trader.strategies import initialize_strategies
from trader.utilities.functions.asset_ohlcv import get_us_dollar
from trader.utilities.functions.cryptocurrency_exchange import (
    fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges,
)
from trader.utilities.logging import logger


def main():
    logger.debug("Initializing tables, views, and base data")
    initialize_models()
    initialize_views()
    initialize_data()
    logger.debug("Loading ISO countries")
    update_countries_from_iso()
    logger.debug("Loading ISO standard currencies")
    update_standard_currencies_from_iso()
    logger.debug("Loading CoinMarketCap cryptocurrency exchange ranks")
    update_cryptocurrency_exchange_ranks_from_coin_market_cap()
    set_initial_enabled_cryptocurrency_exchanges()
    logger.debug("Loading current CoinMarketCap cryptocurrency ranks")
    update_current_cryptocurrency_ranks_from_coin_market_cap(5000)
    set_initial_enabled_quote_assets()
    initialize_strategies()
    set_initial_enabled_strategy_version_instances()
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
        base_asset_ids = fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges(
            session, (e.cryptocurrency_exchange for e in enabled_cryptocurrency_exchanges)
        )
        us_dollar = get_us_dollar(session)
        coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
        one_day = session.query(Timeframe).get(TIMEFRAME_ONE_DAY.fetch_id())
        for base_asset_id in base_asset_ids:
            base_asset = session.query(Asset).get(base_asset_id)
            if base_asset and base_asset.source_id == coin_market_cap_id:
                cryptocurrency = base_asset.cryptocurrency
                if cryptocurrency:
                    logger.debug(
                        "Loading CoinMarketCap cryptocurrency daily USD OHLCV for cryptocurrency %s", base_asset.name
                    )
                    data_retriever = CoinMarketCapAssetOHLCVDataFeedRetriever(
                        base_asset, us_dollar, one_day, cryptocurrency.source_date_added
                    )
                    data_retriever.update_asset_ohlcv()


if __name__ == "__main__":
    main()
