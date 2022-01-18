from typing import Any, Callable, Dict, List, Sequence, Tuple
import pandas as pd
from sqlalchemy.sql import func
from trader.connections.cache import cache
from trader.connections.database import session
from trader.data.initial.data_feed import DATA_FEED_ASSET_OHLCV
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.models.buy_signal import BuySignal
from trader.models.entry_implementation import EntryImplementation, EntryImplementationRun
from trader.models.exit_implementation import ExitImplementation, ExitImplementationRun
from trader.models.position import Position
from trader.models.strategy import StrategyVersionInstance
from trader.models.timeframe import Timeframe
from trader.models.user import User
from trader.tasks import app
from trader.tasks.buy_signal import handle_buy_signal
from trader.utilities.functions import get_asset_us_dollar_id
from trader.utilities.functions.implementation import dataframe_is_valid, fetch_asset_ohlcv_dataframe
from trader.utilities.functions.strategy import fetch_data_feeds_to_strategy_mapping
from trader.utilities.functions.time import TIMEFRAME_UNIT_TO_DELTA_FUNCTION


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
    for strategy in fetch_data_feeds_to_strategy_mapping(True)[data_feed_ids]:
        strategy_version_id = int(cache.get(strategy.get_cache_key()).decode())
        strategy_version_instances = (
            session.query(StrategyVersionInstance).filter_by(strategy_version_id=strategy_version_id).all()
        )
        for strategy_version_instance in strategy_version_instances:
            enabled_strategy_version_instance = strategy_version_instance.enabled_strategy_version_instance
            if not enabled_strategy_version_instance or not enabled_strategy_version_instance.history[0].is_enabled:
                continue
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
            last_date = (
                session.query(func.max(EntryImplementationRun.end_date))
                .select_from(EntryImplementationRun)
                .filter_by(entry_implementation_id=implementation.id)
                .one_or_none()
            )
            if last_date[0]:
                start_date = last_date[0] + TIMEFRAME_UNIT_TO_DELTA_FUNCTION[timeframe.unit](timeframe.amount)
                try:
                    start_index = dataframe.index.tolist().index(start_date)
                except ValueError:
                    continue
            else:
                start_date = dataframe.index[0].to_pydatetime()
                start_index = 0
            implementation_run = EntryImplementationRun(
                entry_implementation_id=implementation.id,
                extra_fields=extra_fields,
                start_date=start_date,
                end_date=dataframe.index[-1].to_pydatetime(),
            )
            session.add(implementation_run)
            session.flush()
            strategy_object = strategy(base_asset_id, strategy_version_instance.arguments)
            strategy_dataframe = strategy_object.enhance_data(dataframe)
            for i in range(start_index, strategy_dataframe.shape[0]):
                buy_signal_strength = strategy_object.get_buy_signal_strength(strategy_dataframe, i)
                if buy_signal_strength:
                    buy_signal = BuySignal(
                        entry_implementation_run_id=implementation_run.id,
                        signal_date=dataframe.index[i],
                        strength=buy_signal_strength,
                    )
                    session.add(buy_signal)
                    session.flush()
                    handle_buy_signal.apply_async(args=(buy_signal.id,), priority=5)
            session.commit()
    users = session.query(User).filter_by(is_live=True).all()
    for user in users:
        positions = session.query(Position).filter_by(user_id=user.id, asset_id=base_asset_id, date_closed=None).all()
        for position in positions:
            for strategy in fetch_data_feeds_to_strategy_mapping(False)[data_feed_ids]:
                strategy_version_id = int(cache.get(strategy.get_cache_key()).decode())
                strategy_version_instances = (
                    session.query(StrategyVersionInstance).filter_by(strategy_version_id=strategy_version_id).all()
                )
                for strategy_version_instance in strategy_version_instances:
                    enabled_strategy_version_instance = strategy_version_instance.enabled_strategy_version_instance
                    if not enabled_strategy_version_instance or enabled_strategy_version_instance.is_disabled:
                        continue
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
