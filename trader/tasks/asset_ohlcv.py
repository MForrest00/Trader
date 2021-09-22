from typing import Optional
from sqlalchemy.sql import func
from trader.connections.database import DBSession
from trader.data.asset_ohlcv.coin_market_cap import CoinMarketCapAssetOHLCVDataFeedRetriever
from trader.data.base import ASSET_TYPE_STANDARD_CURRENCY, SOURCE_COIN_MARKET_CAP, TIMEFRAME_ONE_DAY
from trader.models.asset import Asset
from trader.models.asset_ohlcv import AssetOHLCV, AssetOHLCVGroup, AssetOHLCVPull
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.timeframe import Timeframe
from trader.tasks import app
from trader.utilities.constants import US_DOLLAR_SYMBOL
from trader.utilities.functions import (
    datetime_to_ms_timestamp,
    fetch_base_data_id,
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
    with DBSession() as session:
        base_asset = session.query(Asset).get(base_asset_id)
        us_dollar = (
            session.query(Asset)
            .filter_by(asset_type_id=fetch_base_data_id(ASSET_TYPE_STANDARD_CURRENCY), symbol=US_DOLLAR_SYMBOL)
            .one()
        )
        one_day = session.query(Timeframe).get(fetch_base_data_id(TIMEFRAME_ONE_DAY))
    from_inclusive = ms_timestamp_to_datetime(from_inclusive_ms_timestamp)
    to_exclusive = ms_timestamp_to_datetime(to_exclusive_ms_timestamp) if to_exclusive_ms_timestamp else None
    data_retriever = CoinMarketCapAssetOHLCVDataFeedRetriever(
        base_asset, us_dollar, one_day, from_inclusive, to_exclusive=to_exclusive
    )
    data_retriever.update_asset_ohlcv()


@app.task
def queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task() -> None:
    with DBSession() as session:
        enabled_cryptocurrency_exchanges = (
            session.query(EnabledCryptocurrencyExchange).filter_by(is_disabled=False).all()
        )
        base_asset_ids = fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges(
            session, (e.cryptocurrency_exchange for e in enabled_cryptocurrency_exchanges)
        )
        us_dollar = (
            session.query(Asset)
            .filter_by(asset_type_id=fetch_base_data_id(ASSET_TYPE_STANDARD_CURRENCY), symbol=US_DOLLAR_SYMBOL)
            .one()
        )
        for base_asset_id in base_asset_ids:
            base_asset = session.query(Asset).get(base_asset_id)
            if base_asset and base_asset.source_id == fetch_base_data_id(SOURCE_COIN_MARKET_CAP):
                cryptocurrency = base_asset.cryptocurrency
                if cryptocurrency:
                    last_date = (
                        session.query(func.max(AssetOHLCV.date_open))
                        .select_from(AssetOHLCV)
                        .join(AssetOHLCVPull)
                        .join(AssetOHLCVGroup)
                        .filter(
                            AssetOHLCVGroup.source_id == fetch_base_data_id(SOURCE_COIN_MARKET_CAP),
                            AssetOHLCVGroup.base_asset_id == base_asset.id,
                            AssetOHLCVGroup.quote_asset_id == us_dollar.id,
                            AssetOHLCVGroup.timeframe_id == fetch_base_data_id(TIMEFRAME_ONE_DAY),
                        )
                        .one_or_none()
                    )
                    if last_date:
                        target_date = last_date[0] + TIMEFRAME_UNIT_TO_DELTA_FUNCTION["d"](1)
                    else:
                        target_date = cryptocurrency.source_date_added
                    update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task.delay(
                        base_asset.id, datetime_to_ms_timestamp(target_date)
                    )
