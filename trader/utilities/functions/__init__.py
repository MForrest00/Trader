from datetime import datetime, timedelta
from hashlib import md5
from inspect import getsource, signature
from typing import Callable, Dict, List, Type, Union
from dateutil.relativedelta import relativedelta
from trader.connections.cache import cache
from trader.data.base import (
    AssetTypeData,
    DataFeedData,
    GoogleTrendsGeoData,
    GoogleTrendsGpropData,
    initialize_base_data,
    SourceData,
    SourceTypeData,
    TimeframeData,
    UserData,
)


TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION: Dict[str, Callable[[datetime], datetime]] = {
    "s": lambda x: x.replace(microsecond=0),
    "m": lambda x: x.replace(second=0, microsecond=0),
    "h": lambda x: x.replace(minute=0, second=0, microsecond=0),
    "d": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0),
    "w": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x.weekday()),
    "M": lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    "y": lambda x: x.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
}


TIMEFRAME_UNIT_TO_DELTA_FUNCTION: Dict[str, Callable[[int], Union[timedelta, relativedelta]]] = {
    "s": lambda x: timedelta(seconds=x),
    "m": lambda x: timedelta(minutes=x),
    "h": lambda x: timedelta(hours=x),
    "d": lambda x: timedelta(days=x),
    "w": lambda x: relativedelta(weeks=x),
    "M": lambda x: relativedelta(months=x),
    "y": lambda x: relativedelta(years=x),
}


def clean_range_cap(range_cap: datetime, timeframe_unit: str) -> datetime:
    return TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION[timeframe_unit](range_cap)


def datetime_to_ms_timestamp(datetime_val: datetime) -> int:
    return int(datetime_val.timestamp()) * 1000


def ms_timestamp_to_datetime(timestamp_val: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp_val // 1000)


def iso_time_string_to_datetime(time_string: str) -> datetime:
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def fetch_base_data_id(
    base_data: Union[
        AssetTypeData,
        DataFeedData,
        GoogleTrendsGeoData,
        GoogleTrendsGpropData,
        SourceData,
        SourceTypeData,
        TimeframeData,
        UserData,
    ]
) -> int:
    cache_value = cache.get(base_data.cache_key)
    if not cache_value:
        initialize_base_data()
        cache_value = cache.get(base_data.cache_key)
    return int(cache_value.decode())


def get_init_parameters(source_object: Type) -> List[str]:
    parameters = signature(source_object.__init__).parameters.keys()
    return sorted(list(parameters - set(["self"])))


def get_hash_of_source(source_object: Union[Callable, Type]) -> str:
    return md5(getsource(source_object).encode()).hexdigest()
