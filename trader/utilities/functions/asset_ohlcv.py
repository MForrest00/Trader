from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
from trader.connections.database import DBSession
from trader.models.asset import Asset
from trader.models.asset_ohlcv import AssetOHLCV, AssetOHLCVGroup, AssetOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.utilities.functions import TIMEFRAME_UNIT_TO_DELTA_FUNCTION


def fetch_asset_ohlcv_as_dataframe(
    source: Source,
    base_asset: Asset,
    quote_asset: Asset,
    timeframe: Timeframe,
    from_inclusive: Optional[datetime] = None,
    to_exclusive: Optional[datetime] = None,
) -> pd.DataFrame:
    with DBSession() as session:
        records_query = (
            session.query(AssetOHLCV)
            .join(AssetOHLCVPull)
            .join(AssetOHLCVGroup)
            .filter(
                AssetOHLCVGroup.source_id == source.id,
                AssetOHLCVGroup.base_asset_id == base_asset.id,
                AssetOHLCVGroup.quote_asset_id == quote_asset.id,
                AssetOHLCVGroup.timeframe_id == timeframe.id,
            )
            .order_by(AssetOHLCV.date_open.asc())
        )
        if from_inclusive:
            records_query.filter(AssetOHLCV.date_open >= from_inclusive)
        if to_exclusive:
            records_query.filter(AssetOHLCV.date_open < to_exclusive)
        records = records_query.all()
    return pd.DataFrame(
        (
            {"id": r.id, "open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume}
            for r in records
        ),
        index=(r.date_open for r in records),
    )


def fetch_time_deltas_from_dataframe_index(dataframe: pd.DataFrame) -> List[timedelta]:
    unique_timedeltas = dataframe.index.to_series().diff().dropna().unique()
    return [t.to_pytimedelta() for t in unique_timedeltas]


def dataframe_is_valid(dataframe: pd.DataFrame, timeframe: Timeframe) -> bool:
    if dataframe.shape[0] == 0:
        return False
    delta = TIMEFRAME_UNIT_TO_DELTA_FUNCTION[timeframe.unit](timeframe.amount)
    if timeframe.unit in {"s", "m", "h", "d"}:
        time_deltas = fetch_time_deltas_from_dataframe_index(dataframe)
        if len(time_deltas) != 1:
            return False
        if time_deltas[0] != delta:
            return False
    else:
        for i in range(1, dataframe.shape[0]):
            if dataframe.index[i - 1] + delta != dataframe.index[i]:
                return False
    return True
