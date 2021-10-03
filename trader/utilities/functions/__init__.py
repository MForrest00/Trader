from hashlib import md5
from inspect import getsource, signature
from typing import Callable, List, Type, Union
from trader.connections.cache import cache
from trader.connections.database import session
from trader.data.initial.asset_type import ASSET_TYPE_STANDARD_CURRENCY
from trader.models.asset import Asset
from trader.utilities.constants import DATA_FEED_MESSAGE_DELIMITER, US_DOLLAR_SYMBOL


def get_init_parameters(source_object: Type) -> List[str]:
    parameters = signature(source_object.__init__).parameters.keys()
    return sorted(list(parameters - set(["self"])))


def get_hash_of_source(source_object: Union[Callable, Type]) -> str:
    return md5(getsource(source_object).encode()).hexdigest()


def generate_data_feed_monitor_value(timeframe_id: int, base_asset_id: int, data_feed_id: int) -> str:
    return DATA_FEED_MESSAGE_DELIMITER.join(map(str, (timeframe_id, base_asset_id, data_feed_id)))


def generate_asset_cache_key(asset_type_id: int, symbol: str) -> str:
    return f"asset_{asset_type_id}_{symbol}"


def get_asset_us_dollar() -> Asset:
    standard_currency_id = ASSET_TYPE_STANDARD_CURRENCY.fetch_id()
    cache_key = generate_asset_cache_key(standard_currency_id, US_DOLLAR_SYMBOL)
    us_dollar = (
        session.query(Asset)
        .filter_by(asset_type_id=ASSET_TYPE_STANDARD_CURRENCY.fetch_id(), symbol=US_DOLLAR_SYMBOL)
        .one()
    )
    cache.set(cache_key, us_dollar.id)
    return us_dollar


def get_asset_us_dollar_id() -> int:
    standard_currency_id = ASSET_TYPE_STANDARD_CURRENCY.fetch_id()
    cache_key = generate_asset_cache_key(standard_currency_id, US_DOLLAR_SYMBOL)
    us_dollar_id = cache.get(cache_key)
    if not us_dollar_id:
        us_dollar = get_asset_us_dollar()
        us_dollar_id = us_dollar.id
        cache.set(cache_key, us_dollar_id)
    return us_dollar_id
