from typing import Callable, Dict, List, Sequence, Tuple
import pandas as pd
from trader.connections.database import session
from trader.data.initial.data_feed import DATA_FEED_ASSET_OHLCV
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.data.initial.timeframe import TIMEFRAME_ONE_DAY
from trader.models.timeframe import Timeframe
from trader.tasks import app
from trader.utilities.functions import get_asset_us_dollar_id
from trader.utilities.functions.implementation import dataframe_is_valid, fetch_asset_ohlcv_dataframe


def fetch_one_day_asset_ohlcv_dataframe(timeframe_id: int, base_asset_id: int) -> pd.DataFrame:
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    us_dollar_id = get_asset_us_dollar_id()
    return fetch_asset_ohlcv_dataframe(coin_market_cap_id, base_asset_id, us_dollar_id, timeframe_id)


@app.task
def run_implementations(timeframe_id: int, base_asset_id: int, data_feed_ids: Sequence[int]) -> None:
    data_feed_ids = tuple(data_feed_ids)
    timeframe_one_day_id = TIMEFRAME_ONE_DAY.fetch_id()
    data_feed_asset_ohlcv_id = DATA_FEED_ASSET_OHLCV.fetch_id()
    timeframe_data_feed_to_dataframe_function_mapping: Dict[Tuple[int, int], Callable[[int, int], pd.DataFrame]] = {
        (timeframe_one_day_id, data_feed_asset_ohlcv_id): fetch_one_day_asset_ohlcv_dataframe,
    }
    dataframes: List[pd.DataFrame] = []
    for data_feed_id in data_feed_ids:
        dataframe_function = timeframe_data_feed_to_dataframe_function_mapping[(timeframe_id, data_feed_id)]
        dataframes.append(dataframe_function(timeframe_id, base_asset_id))
    dataframe = dataframes[0]
    for join_dataframe in dataframes[1:]:
        dataframe = dataframe.join(join_dataframe, how="inner")
    timeframe = session.query(Timeframe).get(timeframe_id)
    is_valid = dataframe_is_valid(dataframe, timeframe)
    if not is_valid:
        raise Exception("Invalid values available for buy signal dataframe")
