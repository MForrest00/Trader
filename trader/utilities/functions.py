from datetime import datetime, timedelta
from time import sleep
from typing import Callable, Dict, Set, Sequence, Union
from dateutil.relativedelta import relativedelta
from selenium.webdriver.remote.webdriver import WebDriver
from sqlalchemy.orm import Session
from trader.connections.cache import cache
from trader.data.base import (
    CurrencyTypeData,
    GoogleTrendsPullGeoData,
    GoogleTrendsPullGpropData,
    initialize_base_data,
    SourceData,
    SourceTypeData,
    TimeframeData,
)
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import CryptocurrencyExchangeMarket
from trader.models.enabled_quote_currency import EnabledQuoteCurrency


TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION: Dict[str, Callable[[datetime], datetime]] = {
    "s": lambda x: x.replace(microsecond=0),
    "m": lambda x: x.replace(second=0, microsecond=0),
    "h": lambda x: x.replace(minute=0, second=0, microsecond=0),
    "d": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0),
    "w": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x.weekday()),
    "M": lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    "y": lambda x: x.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
}


TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION: Dict[str, Callable[[datetime, int], datetime]] = {
    "s": lambda x, y: x + timedelta(seconds=y),
    "m": lambda x, y: x + timedelta(minutes=y),
    "h": lambda x, y: x + timedelta(hours=y),
    "d": lambda x, y: x + timedelta(days=y),
    "w": lambda x, y: x + relativedelta(weeks=y),
    "M": lambda x, y: x + relativedelta(months=y),
    "y": lambda x, y: x + relativedelta(years=y),
}


def clean_range_cap(range_cap: datetime, timeframe_unit: str) -> datetime:
    return TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION[timeframe_unit](range_cap)


def datetime_to_ms_timestamp(dt: datetime) -> int:
    return int(dt.timestamp()) * 1000


def ms_timestamp_to_datetime(ts: int) -> datetime:
    return datetime.utcfromtimestamp(ts // 1000)


def iso_time_string_to_datetime(time_string: str) -> datetime:
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def fetch_base_data_id(
    base_data: Union[
        CurrencyTypeData, GoogleTrendsPullGeoData, GoogleTrendsPullGpropData, SourceData, SourceTypeData, TimeframeData
    ]
) -> int:
    cache_value = cache.get(base_data.cache_key)
    if not cache_value:
        initialize_base_data()
        cache_value = cache.get(base_data.cache_key)
    return int(cache_value.decode())


WEB_DRIVER_SCROLL_INCREMENT = 500
WEB_DRIVER_SCROLL_DELAY_SECONDS = 0.5


def fully_scroll_page(web_driver: WebDriver) -> None:
    current_y_offset = web_driver.execute_script("return window.pageYOffset")
    while True:
        web_driver.execute_script(f"window.scrollBy(0, {WEB_DRIVER_SCROLL_INCREMENT})")
        new_y_offset = web_driver.execute_script("return window.pageYOffset")
        if new_y_offset == current_y_offset:
            break
        current_y_offset = new_y_offset
        sleep(WEB_DRIVER_SCROLL_DELAY_SECONDS)


def fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges(
    session: Session, cryptocurrency_exchanges: Sequence[CryptocurrencyExchange]
) -> Set[int]:
    enabled_quote_currencies = session.query(EnabledQuoteCurrency).filter_by(is_disabled=False).all()
    enabled_quote_currency_ids = [c.currency.id for c in enabled_quote_currencies]
    base_currency_ids: Set[int] = set()
    for cryptocurrency_exchange in cryptocurrency_exchanges:
        markets = (
            session.query(CryptocurrencyExchangeMarket)
            .filter(
                CryptocurrencyExchangeMarket.cryptocurrency_exchange_id == cryptocurrency_exchange.id,
                CryptocurrencyExchangeMarket.quote_currency_id.in_(enabled_quote_currency_ids),
                CryptocurrencyExchangeMarket.is_active.is_(True),
            )
            .all()
        )
        for market in markets:
            base_currency_ids.add(market.base_currency_id)
    return base_currency_ids
