from typing import Any, Callable, Dict, List, Sequence, Tuple
import pandas as pd
from trader.connections.database import session
from trader.data.initial.data_feed import DATA_FEED_ASSET_OHLCV
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.models.entry_implementation import EntryImplementation, EntryImplementationRun
from trader.models.exit_implementation import ExitImplementation, ExitImplementationRun
from trader.models.position import Position
from trader.models.strategy import StrategyVersionInstance
from trader.models.timeframe import Timeframe
from trader.models.user import User
from trader.tasks import app
from trader.utilities.functions import get_asset_us_dollar_id
from trader.utilities.functions.implementation import dataframe_is_valid, fetch_asset_ohlcv_dataframe
from trader.utilities.functions.strategy import (
    data_feeds_to_entry_strategy_mapping,
    data_feeds_to_exit_strategy_mapping,
)


def fetch_one_day_asset_ohlcv_dataframe(timeframe_id: int, base_asset_id: int) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    us_dollar_id = get_asset_us_dollar_id()
    extra_fields = {
        "asset_ohlcv_source_id": coin_market_cap_id,
        "asset_ohlcv_quote_asset_id": us_dollar_id,
    }
    return fetch_asset_ohlcv_dataframe(coin_market_cap_id, base_asset_id, us_dollar_id, timeframe_id), extra_fields


@app.task
def run_implementations(timeframe_id: int, base_asset_id: int, data_feed_ids: Sequence[int]) -> None:
    data_feed_ids = tuple(data_feed_ids)
    timeframe_one_day_id = TIMEFRAME_ONE_DAY.fetch_id()
    data_feed_asset_ohlcv_id = DATA_FEED_ASSET_OHLCV.fetch_id()
    timeframe_data_feed_to_dataframe_function_mapping: Dict[
        Tuple[int, int], Callable[[int, int], Tuple[pd.DataFrame, Dict[str, Any]]]
    ] = {
        (timeframe_one_day_id, data_feed_asset_ohlcv_id): fetch_one_day_asset_ohlcv_dataframe,
    }
    dataframes: List[pd.DataFrame] = []
    extra_fields: Dict[str, Any] = {}
    for data_feed_id in data_feed_ids:
        dataframe_function = timeframe_data_feed_to_dataframe_function_mapping[(timeframe_id, data_feed_id)]
        data_feed_dataframe, data_feed_extra_fields = dataframe_function(timeframe_id, base_asset_id)
        dataframes.append(data_feed_dataframe)
        extra_fields.update(data_feed_extra_fields)
    dataframe = dataframes[0]
    for join_dataframe in dataframes[1:]:
        dataframe = dataframe.join(join_dataframe, how="inner")
    timeframe = session.query(Timeframe).get(timeframe_id)
    is_valid = dataframe_is_valid(dataframe, timeframe)
    if not is_valid:
        raise Exception("Invalid values available for buy signal dataframe")
    for strategy_version_id in data_feeds_to_entry_strategy_mapping[data_feed_ids]:
        strategy_version_instances = (
            session.query(StrategyVersionInstance).filter_by(strategy_version_id=strategy_version_id).all()
        )
        for strategy_version_instance in strategy_version_instances:
            implementation = session.query(EntryImplementation).filter_by(
                timeframe_id=timeframe_id,
                base_asset_id=base_asset_id,
                strategy_version_instance_id=strategy_version_instance.id,
            )
            if not implementation:
                implementation = EntryImplementation(
                    timeframe_id=timeframe_id,
                    base_asset_id=base_asset_id,
                    strategy_version_instance_id=strategy_version_instance.id,
                )
                session.add(implementation)
                session.flush()
    users = session.query(User).filter_by(is_live=True).all()
    for user in users:
        positions = session.query(Position).filter_by(user_id=user.id, asset_id=base_asset_id, date_closed=None).all()
        for position in positions:
            for strategy_version_id in data_feeds_to_exit_strategy_mapping[data_feed_ids]:
                strategy_version_instances = (
                    session.query(StrategyVersionInstance).filter_by(strategy_version_id=strategy_version_id).all()
                )
                for strategy_version_instance in strategy_version_instances:
                    implementation = session.query(ExitImplementation).filter_by(
                        timeframe_id=timeframe_id,
                        position_id=position.id,
                        strategy_version_instance_id=strategy_version_instance.id,
                    )
                    if not implementation:
                        implementation = ExitImplementation(
                            timeframe_id=timeframe_id,
                            position_id=position.id,
                            strategy_version_instance_id=strategy_version_instance.id,
                        )
                        session.add(implementation)
                        session.flush()
