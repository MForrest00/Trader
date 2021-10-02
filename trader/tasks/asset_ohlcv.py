from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.sql import func
from trader.connections.cache import cache
from trader.connections.database import session
from trader.data.asset_ohlcv.coin_market_cap import CoinMarketCapAssetOHLCVDataFeedRetriever
from trader.data.initial.data_feed import DATA_FEED_ASSET_OHLCV
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.models.asset import Asset
from trader.models.asset_ohlcv import AssetOHLCV, AssetOHLCVGroup, AssetOHLCVPull
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.timeframe import Timeframe
from trader.tasks import app
from trader.utilities.constants import DATA_DEFAULT_FLOOR, DATA_FEED_MONITOR_QUEUE_KEY
from trader.utilities.functions import (
    clean_range_cap,
    datetime_to_ms_timestamp,
    generate_data_feed_monitor_value,
    get_asset_us_dollar,
    get_asset_us_dollar_id,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_DELTA_FUNCTION,
)
from trader.utilities.functions.cryptocurrency_exchange import (
    fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges,
)


@app.task
def update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task(
    base_asset_id: int, from_inclusive_ms_timestamp: int, to_exclusive_ms_timestamp: Optional[int] = None
) -> None:
    base_asset = session.query(Asset).get(base_asset_id)
    us_dollar = get_asset_us_dollar()
    one_day = TIMEFRAME_ONE_DAY.get_instance()
    from_inclusive = ms_timestamp_to_datetime(from_inclusive_ms_timestamp)
    to_exclusive = ms_timestamp_to_datetime(to_exclusive_ms_timestamp) if to_exclusive_ms_timestamp else None
    data_retriever = CoinMarketCapAssetOHLCVDataFeedRetriever(
        base_asset, us_dollar, one_day, from_inclusive, to_exclusive=to_exclusive
    )
    new_records_inserted = data_retriever.update_asset_ohlcv()
    if new_records_inserted:
        value = generate_data_feed_monitor_value(one_day.id, base_asset_id, DATA_FEED_ASSET_OHLCV.fetch_id())
        cache.rpush(DATA_FEED_MONITOR_QUEUE_KEY, value)


@app.task
def queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task() -> None:
    enabled_cryptocurrency_exchanges = session.query(EnabledCryptocurrencyExchange).filter_by(is_disabled=False).all()
    base_asset_ids = fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges(
        (e.cryptocurrency_exchange for e in enabled_cryptocurrency_exchanges)
    )
    us_dollar_id = get_asset_us_dollar_id()
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    one_day_id = TIMEFRAME_ONE_DAY.fetch_id()
    for base_asset_id in base_asset_ids:
        base_asset = session.query(Asset).get(base_asset_id)
        if base_asset and base_asset.cryptocurrency:
            last_date = (
                session.query(func.max(AssetOHLCV.date_open))
                .select_from(AssetOHLCV)
                .join(AssetOHLCVPull)
                .join(AssetOHLCVGroup)
                .filter(
                    AssetOHLCVGroup.source_id == coin_market_cap_id,
                    AssetOHLCVGroup.base_asset_id == base_asset.id,
                    AssetOHLCVGroup.quote_asset_id == us_dollar_id,
                    AssetOHLCVGroup.timeframe_id == one_day_id,
                )
                .one_or_none()
            )
            timedelta = TIMEFRAME_UNIT_TO_DELTA_FUNCTION[TIMEFRAME_ONE_DAY.unit](TIMEFRAME_ONE_DAY.amount)
            if last_date:
                target_date = last_date[0] + timedelta
            else:
                target_date = base_asset.cryptocurrency.coin_market_cap_date_added or DATA_DEFAULT_FLOOR
            if datetime.now(timezone.utc) - clean_range_cap(target_date, TIMEFRAME_ONE_DAY.unit) >= timedelta:
                update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task.apply_async(
                    (base_asset.id, datetime_to_ms_timestamp(target_date)), priority=3
                )
